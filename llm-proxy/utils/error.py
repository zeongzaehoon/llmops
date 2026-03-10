from functools import wraps
from fastapi.responses import StreamingResponse, JSONResponse

from utils.response import Response500



class AppError(Exception):

    def __init__(self, message, code=None, status=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

    def to_dict(self):
        return {
            "message": self.message,
            "status": self.status,
            "code": self.code
        }

class FirstTryError(AppError):

    def __init__(self):
        super().__init__("First try error occurred")

class SecondTryError(AppError):

    def __init__(self):
        super().__init__("Second try error occurred")


class ProxyServerError(AppError):

    def __init__(self):
        super().__init__("Proxy server error occurred")


class OverTokenLimitError(AppError):

    def __init__(self, context_window: int, token_count: int):
        super().__init__("Over token limit error occurred")
        self.context_window = context_window
        self.token_count = token_count
        self.message = f"죄송합니다. 토큰 제한을 초과했습니다. 보내주신 토큰은 {token_count}개이고, 저희 모델이 허용할 수 있는 컨텍스트 윈도우는 {context_window}개입니다. 해당 메세지를 받으셨다면 담당자에게 문의해주시길 바랍니다."


class FileError(AppError):

    def __init__(self):
        super().__init__("FileSearch Error")



def make_error_message_generator(message: str=None):
    message = message if message else "죄송합니다. PROXY SERVER에 문제가 발생했습니다. 해당 메세지를 받으셨다면 담당자에게 문의해주시길 바랍니다."
    for chunk in message:
        yield chunk


def handle_errors():
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            try:
                return await f(*args, **kwargs)

            except ProxyServerError:
                return StreamingResponse(
                    make_error_message_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Content-Type": "text/event-stream; charset=utf-8",
                        "Cache-Control": "no-cache",
                        "Transfer-Encoding": "chunked"
                    }
                )

            except OverTokenLimitError as e:
                return StreamingResponse(
                    make_error_message_generator(e.message),
                    media_type="text/event-stream",
                    headers={
                        "Content-Type": "text/event-stream; charset=utf-8",
                        "Cache-Control": "no-cache",
                        "Transfer-Encoding": "chunked"
                    }
                )

            except FileError as e:
                return Response500(message=e.message).to_orjson()

            except Exception as e:
                content = {
                    "message": "죄송합니다. 문제가 발생했습니다. 해당 메세지를 받으셨다면 담당자에게 문의해주시길 바랍니다.",
                    "status": "error",
                    "code": "599"
                }
                return JSONResponse(content=content, status_code=599)

        return decorated_function
    return decorator
