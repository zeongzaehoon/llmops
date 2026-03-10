import asyncio
import uuid
from dataclasses import dataclass
from typing import Any

from fastapi.responses import ORJSONResponse


class ResponseQueue:
	def __init__(self, request_id: str):
		self.event = asyncio.Event()
		self.queue = asyncio.Queue()
		self.request_id = request_id or uuid.uuid4()


def get_response_queue():
	return ResponseQueue(request_id=str(uuid.uuid4()))


@dataclass
class ResponseModel:
	code: int = None
	data: Any = None
	message: str = None

	def to_dict(self):
		return {
			"code": self.code,
			"data": self.data,
			"message": self.message
		}

	def to_orjson(self):
		return ORJSONResponse(content=self.to_dict(), status_code=self.code)


@dataclass
class Response200(ResponseModel):
	code: int = 200
	def __post_init__(self):
		self.code = 200

@dataclass
class Response500(ResponseModel):
	code: int = 500
	def __post_init__(self):
		self.code = 500

@dataclass
class Response400(ResponseModel):
	code: int = 400
	def __post_init__(self):
		self.code = 400

@dataclass
class Response401(ResponseModel):
	code: int = 401
	def __post_init__(self):
		self.code = 401

@dataclass
class Response403(ResponseModel):
	code: int = 403
	def __post_init__(self):
		self.code = 403

@dataclass
class Response404(ResponseModel):
	code: int = 404
	def __post_init__(self):
		self.code = 404
