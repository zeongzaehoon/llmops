"""
Phase 1 characterization tests (Task #15).

Pins the behavior of `translate_conversation_history` across the OpenAI-family
provider clients (open_ai / azure / fourgrit / local) BEFORE extracting the
shared logic into client.common. These 4 implementations are byte-identical
today; this suite guarantees the extraction preserves behavior exactly.

Clients are built via __new__ (no __init__) so no API key / network is needed —
the method only reads self.data.conversation_history.
"""
import pytest

from models.llm import ChatPayload
from client.open_ai import OpenAIClient
from client.azure import AzureClient
from client.fourgrit import FourgritClient
from client.local import LocalClient

OPENAI_FAMILY = [OpenAIClient, AzureClient, FourgritClient, LocalClient]


def _translate(client_cls, history):
    payload = ChatPayload(service="test", question="q", conversationHistory=history)
    instance = client_cls.__new__(client_cls)  # bypass __init__ (no env/network)
    instance.data = payload
    return instance.translate_conversation_history()


# (label, input conversation_history, expected output)
CASES = [
    ("none", None, None),
    ("empty", [], None),
    (
        "full_pair_message_key_role_aliases",
        [{"role": "human", "message": "hi"}, {"role": "ai", "message": "hello"}],
        [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
    ),
    (
        "canonical_roles_content_key",
        [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}],
        [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}],
    ),
    (
        "two_pairs",
        [
            {"role": "human", "message": "q1"},
            {"role": "ai", "message": "a1"},
            {"role": "human", "message": "q2"},
            {"role": "ai", "message": "a2"},
        ],
        [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "q2"},
            {"role": "assistant", "content": "a2"},
        ],
    ),
    ("unpaired_trailing_user_dropped", [{"role": "human", "message": "hi"}], None),
    ("leading_assistant_without_user_dropped", [{"role": "ai", "message": "x"}], None),
    (
        "assistant_uses_latest_pending_user",
        [
            {"role": "human", "message": "q1"},
            {"role": "human", "message": "q2"},
            {"role": "ai", "message": "a"},
        ],
        [{"role": "user", "content": "q2"}, {"role": "assistant", "content": "a"}],
    ),
]


@pytest.mark.parametrize("client_cls", OPENAI_FAMILY, ids=lambda c: c.__name__)
@pytest.mark.parametrize("label,history,expected", CASES, ids=[c[0] for c in CASES])
def test_translate_conversation_history(client_cls, label, history, expected):
    assert _translate(client_cls, history) == expected


def test_all_openai_family_agree():
    """All 4 clients must produce identical output for identical input."""
    for label, history, _expected in CASES:
        outputs = [_translate(c, history) for c in OPENAI_FAMILY]
        assert all(o == outputs[0] for o in outputs), f"divergence on case={label}: {outputs}"
