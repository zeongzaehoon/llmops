"""Characterization: utils/error.py custom exception hierarchy."""
import pytest

from utils.error import (
    AppError, LLMProxyError, AWSError, MessageQueueError, VectorDBError,
    DBError, MemoryDBError, DataError, OverTokenError, ForbiddenError,
    LLMStreamingError, TokenError,
)

FAIL, INVALID, OK = 500, 400, 200


def test_apperror_base_contract():
    e = AppError("msg")
    assert isinstance(e, Exception)
    assert e.message == "msg"
    assert e.code == 500
    assert e.status == "ERROR"
    assert e.to_dict() == {"message": "msg", "status": "ERROR", "code": 500}


@pytest.mark.parametrize("cls,code", [
    (LLMProxyError, FAIL),
    (AWSError, FAIL),
    (MessageQueueError, FAIL),
    (VectorDBError, FAIL),
    (DBError, FAIL),
    (MemoryDBError, FAIL),
    (DataError, INVALID),
    (OverTokenError, OK),
    (ForbiddenError, OK),
    (LLMStreamingError, OK),
    (TokenError, 401),
])
def test_subclasses_are_apperrors_with_expected_code(cls, code):
    e = cls()
    assert isinstance(e, AppError)
    assert e.code == code
    assert e.message  # each defines a default message
    assert e.to_dict()["code"] == code


def test_custom_message_is_preserved():
    e = DBError("specific failure")
    assert e.message == "specific failure"
    assert e.code == 500
