from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResBody(BaseModel):
	code: int = 200
	message: str | None = None
	data: Any = None

	def to_response(self) -> JSONResponse:
		"""HTTP status code를 code 필드와 일치시켜야 할 때 사용 (에러 응답 등)"""
		return JSONResponse(content=self.model_dump(), status_code=self.code)


class Res200(ResBody):
	code: int = 200

class Res400(ResBody):
	code: int = 400

class Res401(ResBody):
	code: int = 401

class Res403(ResBody):
	code: int = 403

class Res404(ResBody):
	code: int = 404

class Res500(ResBody):
	code: int = 500


class TokenRes(BaseModel):
	res: ResBody
	access_token: str
	refresh_token: str | None = None