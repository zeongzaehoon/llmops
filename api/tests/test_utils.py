"""Characterization: infra-free utils (date, vector/tiktoken)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from utils.date import get_utc_now
from utils.vector import get_token_length, chunking_text
from utils.constants import TIKTOKEN_MODEL_LIST


def test_get_utc_now_is_utc_and_current():
    now = get_utc_now()
    assert now.tzinfo == ZoneInfo("UTC")
    assert abs((datetime.now(timezone.utc) - now).total_seconds()) < 5


def test_token_length_empty_is_zero():
    assert get_token_length("") == 0


def test_token_length_grows_with_text():
    short = get_token_length("hello")
    longer = get_token_length("hello world this is a noticeably longer sentence")
    assert isinstance(short, int) and short > 0
    assert longer > short


def test_token_length_unknown_model_falls_back():
    # model not in TIKTOKEN_MODEL_LIST -> falls back to TIKTOKEN_MODEL_LIST[0]
    assert get_token_length("hello", model_name="totally-unknown-model") > 0


def test_chunking_covers_text_in_multiple_chunks():
    text = " ".join(str(i) for i in range(200))
    chunks = chunking_text(
        text, model_name=TIKTOKEN_MODEL_LIST[0], max_tokens=20, overlap_tokens=5,
    )
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)
