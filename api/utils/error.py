from functools import wraps
import logging
import time

from fastapi import FastAPI, Request

from .constants import *
from .response import *


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
                return Response500(message="[OverTokenError] ::: Over Token Size")

            # client Error
            except AWSError as e:
                logging.error(f"[AWSError] ::: {e}")
                return Response500(message="[AWSError] ::: AWS Error")

            except VectorDBError as e:
                logging.error(f"[VectorDBError] ::: {e}")
                return Response500(message="[VectorDBError] ::: Vector DB Error")

            except DBError as e:
                logging.error(f"[DBError] ::: {e}")
                return Response500(message="[DBError] ::: DB Error")

            except MemoryDBError as e:
                logging.error(f"[MemoryDBError] ::: {e}")
                return Response500(message="[MemoryDBError] ::: Memory DB Error")

            # Token Error
            except TokenError as e:
                logging.error(f"[TokenError] ::: {e}")
                return ORJSONResponse(content="[TokenError] ::: Token Error", status_code=401)

            # route side Error
            except ForbiddenError as e:
                logging.error(f"[ForbiddenError] ::: {e}")
                return Response403(message="[ForbiddenError] ::: Forbidden Error")

            except DataError as e:
                logging.error(f"[DataError] ::: {e}")
                return Response400(message="[DataError] ::: Data Error")

            except Exception as e:
                logging.error(f"[Exception] ::: {e}")
                return Response500(message="[Exception] ::: Exception")
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
        return ORJSONResponse(
            status_code=401,
            content={
                "res": {
                    "code": 401,
                    "message": str(exc),
                    "data": None
                }
            }
        )
