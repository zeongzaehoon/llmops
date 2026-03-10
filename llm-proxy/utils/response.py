from typing import Any
from dataclasses import dataclass

from fastapi.responses import ORJSONResponse



@dataclass
class ResponseModel:
    code: int = None
    data: Any = None
    message: str = None
    date_format: str = "flask"

    def to_dict(self):
        return {
            "code": self.code,
            "data": self.data,
            "message": self.message
        }

    def to_orjson(self):
        return ORJSONResponse(
            {
                "code": self.code,
                "data": self.data,
                "message": self.message
            }
        )

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
