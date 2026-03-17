from functools import wraps
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .constants import *
from response import Res400, Res401, Res403, Res500


SUCCESS_CODE = 200
FAIL_CODE = 500
INVALID_DATA_CODE = 400


def handle_errors():
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            try:
                return await f(*args, **kwargs)

            # Token Error
            except OverTokenError as e:
                logging.error(f"[OverTokenError] ::: {e}")
                return Res500(message="[OverTokenError] ::: Over Token Size").to_response()

            # client Error
            except AWSError as e:
                logging.error(f"[AWSError] ::: {e}")
                return Res500(message="[AWSError] ::: AWS Error").to_response()

            except VectorDBError as e:
                logging.error(f"[VectorDBError] ::: {e}")
                return Res500(message="[VectorDBError] ::: Vector DB Error").to_response()

            except DBError as e:
                logging.error(f"[DBError] ::: {e}")
                return Res500(message="[DBError] ::: DB Error").to_response()

            except MemoryDBError as e:
                logging.error(f"[MemoryDBError] ::: {e}")
                return Res500(message="[MemoryDBError] ::: Memory DB Error").to_response()

            # Token Error
            except TokenError as e:
                logging.error(f"[TokenError] ::: {e}")
                return Res401(message="[TokenError] ::: Token Error").to_response()

            # route side Error
            except ForbiddenError as e:
                logging.error(f"[ForbiddenError] ::: {e}")
                return Res403(message="[ForbiddenError] ::: Forbidden Error").to_response()

            except DataError as e:
                logging.error(f"[DataError] ::: {e}")
                return Res400(message="[DataError] ::: Data Error").to_response()

            except Exception as e:
                logging.error(f"[Exception] ::: {e}")
                return Res500(message="[Exception] ::: Exception").to_response()
        return decorated_function
    return decorator


class AppError(Exception):

    def __init__(self, message, code=None, status=None):
        super().__init__(message)
        self.message = message
        self.code = code or 500
        self.status = status or "ERROR"

    def to_dict(self):
        return {
            "message": self.message,
            "status": self.status,
            "code": self.code
        }

class LLMProxyError(AppError):

    def __init__(self, message="LLM proxy error occurred"):
        super().__init__(message, code=FAIL_CODE)


class AWSError(AppError):

    def __init__(self, message="AWS error occurred"):
        super().__init__(message, code=FAIL_CODE)


class MessageQueueError(AppError):

    def __init__(self, message="Message queue error occurred"):
        super().__init__(message, code=FAIL_CODE)


class VectorDBError(AppError):

    def __init__(self, message="Vector database error occurred"):
        super().__init__(message, code=FAIL_CODE)


class DBError(AppError):

    def __init__(self, message="Database error occurred"):
        super().__init__(message, code=FAIL_CODE)


class MemoryDBError(AppError):

    def __init__(self, message="Memory database error occurred"):
        super().__init__(message, code=FAIL_CODE)


class DataError(AppError):

    def __init__(self, message="Invalid data provided"):
        super().__init__(message, code=INVALID_DATA_CODE)


class OverTokenError(AppError):

    def __init__(self, message="is over token size"):
        super().__init__(message, code=SUCCESS_CODE)


class InvalidTokenError(AppError):

    def __init__(self, message="Invalid token provided"):
        super().__init__(message, code=SUCCESS_CODE)

class NoQuestionError(AppError):

    def __init__(self, message="No Question"):
        super().__init__(message, code=SUCCESS_CODE)

class NoChatbotKeyError(AppError):

    def __init__(self, message="No Chatbot Key"):
        super().__init__(message, code=SUCCESS_CODE)

class NoChatbotRefererError(AppError):

    def __init__(self, message="No Chatbot Referer"):
        super().__init__(message, code=SUCCESS_CODE)

class ParserCreditAvailableOverError(AppError):

    def __init__(self, message="Parser Credit Available"):
        super().__init__(message, code=SUCCESS_CODE)

class ExpiredPlanChatError(AppError):

    def __init__(self, message="Expired Plan Chat"):
        super().__init__(message, code=SUCCESS_CODE)

class ExpiredPlanError(AppError):

    def __init__(self, message="Expired Plan Error"):
        super().__init__(message, code=SUCCESS_CODE)

class ForbiddenError(AppError):

    def __init__(self, message="Forbidden Error"):
        super().__init__(message, code=SUCCESS_CODE)

class LLMStreamingError(AppError):

    def __init__(self, message="LLM proxy streaming error occurred"):
        super().__init__(message, code=SUCCESS_CODE)

class TokenError(AppError):

    def __init__(self, message="Token Error"):
        super().__init__(message, code=401)

# global token error handler
def token_exception_handler(app: FastAPI):
    @app.exception_handler(TokenError)
    async def token_error_handler(request: Request, exc: TokenError):
        return JSONResponse(
            status_code=401,
            content={
                "res": Res401(message=str(exc)).model_dump()
            }
        )