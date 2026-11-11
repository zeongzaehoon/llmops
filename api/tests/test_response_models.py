"""Characterization: response/ Pydantic envelope models."""
from fastapi.responses import JSONResponse

from response.model import (
    ResBody, Res200, Res400, Res401, Res403, Res404, Res500, TokenRes,
)


def test_status_classes_carry_their_http_code():
    assert Res200().code == 200
    assert Res400().code == 400
    assert Res401().code == 401
    assert Res403().code == 403
    assert Res404().code == 404
    assert Res500().code == 500


def test_resbody_defaults():
    r = ResBody()
    assert r.code == 200
    assert r.message is None
    assert r.data is None


def test_model_dump_shape():
    r = Res200(message="ok", data={"x": 1})
    assert r.model_dump() == {"code": 200, "message": "ok", "data": {"x": 1}}


def test_to_response_aligns_http_status_with_code():
    resp = Res500(message="boom").to_response()
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 500


def test_token_res_structure():
    t = TokenRes(res=Res200(message="access"), access_token="a", refresh_token="r")
    d = t.model_dump()
    assert d["access_token"] == "a"
    assert d["refresh_token"] == "r"
    assert d["res"]["code"] == 200


def test_token_res_refresh_is_optional():
    t = TokenRes(res=Res200(), access_token="a")
    assert t.refresh_token is None
