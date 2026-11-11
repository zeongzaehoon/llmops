"""Characterization: payload/ Pydantic request schemas (alias + validation)."""
import pytest
from pydantic import ValidationError

from payload.vector import (
    upsertPayload, searchPayload, deleteIdPayload, deleteFilterPayload,
)


def test_upsert_accepts_alias_and_field_name():
    by_alias = upsertPayload(index="idx", id="1", content="c", metadata={"a": 1})
    assert by_alias.index_name == "idx"
    by_name = upsertPayload(index_name="idx", id="1", content="c", metadata={})
    assert by_name.index_name == "idx"


def test_search_defaults():
    p = searchPayload(index="idx", search="q")
    assert p.query == "q"
    assert p.k == 4
    assert p.filter is None


def test_missing_required_field_raises():
    with pytest.raises(ValidationError):
        upsertPayload(id="1", content="c", metadata={})  # missing index


def test_delete_id_alias():
    p = deleteIdPayload(id="1", index="idx")
    assert p.index_name == "idx"


def test_delete_filter_requires_dict():
    p = deleteFilterPayload(filter={"k": "v"}, index="idx")
    assert p.filter == {"k": "v"}
    with pytest.raises(ValidationError):
        deleteFilterPayload(filter="not-a-dict", index="idx")
