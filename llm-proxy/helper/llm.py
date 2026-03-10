import re
import base64
import logging
from urllib.parse import urlparse
from asyncio import Queue
from client.common import detect_image_format
import asyncio
from concurrent.futures import ThreadPoolExecutor
_executor = ThreadPoolExecutor(max_workers=4) # 전역으로 설정

from client.azure import AzureClient
from client.open_ai import OpenAIClient
from client.bedrock import BedrockClient
from client.anthropic import AnthropicClient
from client.x import XClient
from client.google import GoogleClient
from client.fourgrit import FourgritClient

from utils.constants import *
from utils.error import FirstTryError, SecondTryError, ProxyServerError, OverTokenLimitError
from utils.vector import get_token_length
from models.llm import *



def check_token_length(payload: ChatPayload | OcrChatPayload | ChatMCPPayload):
    try:
        input_message = payload.system_message
        if payload.question:
            input_message = input_message + payload.question
        if payload.conversation_history:
            input_message = input_message + str(payload.conversation_history)
        if payload.system_message_placeholder:
            try:
                input_message = input_message.format_map(payload.system_message_placeholder)
            except:
                input_message = input_message + str(payload.system_message_placeholder)
        token_length = get_token_length(input_message, payload.model)

    except Exception as e:
        logging.error(f"[helper.llm.check_token_length] error: {e}")
        raise ProxyServerError()

    if payload.model in OPENAI_REASONING_MODEL_LIST or payload.model in ANTHROPIC_MODEL_LIST:
        if token_length > 200000:
            logging.error(f"session_key: {payload.session_key} | [helper.llm.check_token_length] context is too long for {payload}")
            logging.error(f"token_length: {token_length}")
            raise OverTokenLimitError(context_window=200000, token_count=token_length)
    else:
        if token_length > 128000:
            logging.error(f"session_key: {payload.session_key} | [helper.llm.check_token_length] context is too long for {payload}")
            logging.error(f"token_length: {token_length}")
            raise OverTokenLimitError(context_window=128000, token_count=token_length)


def set_client(
        payload: ChatPayload | OcrChatPayload,
        openai_client: OpenAIClient,
        azure_client: AzureClient,
        bedrock_client: BedrockClient,
        anthropic_client: AnthropicClient,
        x_client: XClient,
        google_client: GoogleClient
):

    if payload.vendor == OPENAI:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: OpenAI")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: Azure")
        first_try_client = openai_client
        second_try_client = azure_client
    elif payload.vendor == AZURE:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: Azure")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: OpenAI")
        first_try_client = azure_client
        second_try_client = openai_client
    elif payload.vendor == ANTHROPIC:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: Anthropic")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: Bedrock")
        first_try_client = anthropic_client
        second_try_client = bedrock_client
    elif payload.vendor == BEDROCK:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: Bedrock")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: Anthropic")
        first_try_client = bedrock_client
        second_try_client = anthropic_client
    elif payload.vendor == XAI:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: XAI")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: OpenAI")
        first_try_client = x_client
        second_try_client = openai_client
    elif payload.vendor == GOOGLE:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set first client: GOOGLE")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_client] set second client: OpenAI")
        first_try_client = google_client
        second_try_client = openai_client
    else:
        first_try_client = openai_client
        second_try_client = anthropic_client

    return first_try_client, second_try_client


def set_mcp_client(
        payload: ChatMCPPayload,
        bedrock_client: BedrockClient,
        anthropic_client: AnthropicClient,
        google_client: GoogleClient
):
    if payload.vendor == ANTHROPIC:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set first client: Anthropic")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set second client: Bedrock")
        first_try_client = anthropic_client
        second_try_client = bedrock_client
    elif payload.vendor == BEDROCK:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set first client: Bedrock")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set second client: Anthropic")
        first_try_client = bedrock_client
        second_try_client = anthropic_client
    elif payload.vendor == GOOGLE:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set first client: GOOGLE")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set second client: OpenAI")
        first_try_client = google_client
        second_try_client = bedrock_client
    else:
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] vendor is not supported. payload.vendor: {payload.vendor}")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set first client: Bedrock")
        logging.info(f"session_key: {payload.session_key} | [helper.llm.set_mcp_client] set second client: Anthropic")
        first_try_client = bedrock_client
        second_try_client = anthropic_client

    return first_try_client, second_try_client


async def safe_stream(first_client, second_client, session_key=None):
    try:
        async for chunk in first_client.stream(is_retry=False):
            yield chunk

    except FirstTryError:
        try:
            async for chunk in second_client.stream(is_retry=True):
                yield chunk

        except ProxyServerError as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] ProxyServerError: {e}")
            raise ProxyServerError()

        except OverTokenLimitError as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] OverTokenLimitError: {e}")
            raise OverTokenLimitError()

        except Exception as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] Exception: {e}")
            raise ProxyServerError()


async def safe_stream_with_mcp(first_client, second_client, session_key=None):
    try:
        async for chunk in first_client.stream_with_mcp(is_retry=False):
            yield chunk

    except FirstTryError:
        try:
            async for chunk in second_client.stream_with_mcp(is_retry=True):
                yield chunk

        except ProxyServerError as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] error: {e.message}")
            raise ProxyServerError()

        except OverTokenLimitError as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] error: {e.message}")
            raise ProxyServerError()

        except Exception as e:
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] second try is failed. send error message to client")
            logging.error(f"session_key: {session_key} | [helper.llm.safe_stream] error: {e}")
            raise ProxyServerError()


async def safe_chat(first_client, second_client, session_key=None):
    try:
        result = await first_client.chat()
        return result
    except FirstTryError:
        try:
            result = await second_client.chat(is_retry=True)
            return result
        except Exception as e:
            logging.error("[helper.llm.safe_function_call] second try is failed. send error message to client")
            logging.error(f"[helper.llm.safe_function_call] error: {e}")
            raise ProxyServerError()


async def safe_function_call(first_client, second_client):
    try:
        return await first_client.function_call()
    except FirstTryError:
        try:
            return await second_client.function_call(is_retry=True)
        except Exception as e:
            logging.error("[helper.llm.safe_function_call] second try is failed. send error message to client")
            logging.error(f"[helper.llm.safe_function_call] error: {e}")
            raise ProxyServerError()


async def safe_embeddings(
        first_client: OpenAIClient | AzureClient | FourgritClient,
        second_client: OpenAIClient | AzureClient | FourgritClient
):
    try:
        logging.info("[helper.llm.safe_embeddings] FirstTry: openAI")
        return await first_client.embeddings(is_retry=False)
    except FirstTryError:
        try:
            logging.info("[helper.llm.safe_embeddings] SecondTry: Azure")
            return await second_client.embeddings(is_retry=True)
        except SecondTryError:
            logging.error("[helper.llm.safe_embeddings] second try is failed. send error message to client")
            raise ProxyServerError()
        except Exception as e:
            logging.error("[helper.llm.safe_embeddings] second try is failed. send error message to client")
            logging.error(f"[helper.llm.safe_embeddings] error: {e}")
            raise ProxyServerError()


async def stream_from_queue(queue:Queue):
    while True:
        chunk = await queue.get()
        if chunk is None:
            break
        yield chunk


def clear_data_in_base64(text:str):
    text = text.strip()
    if text.startswith('data:'):
        text = text.split(',', 1)[1] if ',' in text else text
    return text


def detect_image_type(data: str):
    """
    Returns: type must be 'url' or 'base64'
    """
    data = data.strip()

    if is_valid_url(data):
        return 'url'
    elif is_base64(data):
        return 'base64'
    else:
        logging.error(f"[helper.llm.check_is_in_only_base64_and_url] is detected invalid images value: {data}")
        raise ProxyServerError


def is_valid_url(text: str):
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https', 's3']
    except:
        return False

def is_base64(text: str):
    base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
    if not base64_pattern.match(text):
        return False

    try:
        base64.b64decode(text, validate=True)
        return True
    except:
        return False


def check_is_in_only_base64_and_url(image_types:list):
    allowed_values = {BASE64, URL}
    image_types_set = set(image_types)
    if invalid := image_types_set - allowed_values:
        logging.error(f"[helper.llm.check_is_in_only_base64_and_url] is detected invalid image type value: {invalid}")
        raise ProxyServerError


def _get_extension_sync(image_data: bytes) -> str:
    try:
        extension = detect_image_format(image_data)
        return extension
    except Exception as e:
        logging.error(f"[helper.llm._get_image_extension] Failed to process image: {e}")
        return "error"


async def get_image_extension(images: list[str], image_types: list[str]) -> list[str]:
    # 결과 초기화
    extensions = [None] * len(images)

    # base64 이미지 수집
    tasks = []
    task_indices = []

    for idx, (image, img_type) in enumerate(zip(images, image_types)):
        if img_type == BASE64:
            try:
                # 디코딩
                if ',' in image:
                    image = image.split(',', 1)[1]
                decoded = base64.b64decode(image)

                # 비동기 태스크 생성
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(
                    _executor,
                    _get_extension_sync,
                    decoded
                )
                tasks.append(task)
                task_indices.append(idx)

            except Exception as e:
                logging.error(f"[helper.llm.get_image_extension] Base64 decode failed at index {idx}: {e}")
                extensions[idx] = "error"

    # 병렬 처리
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 매핑
        for idx, result in zip(task_indices, results):
            if isinstance(result, Exception):
                logging.error(f"Processing failed at index {idx}: {result}")
                extensions[idx] = "error"
            else:
                extensions[idx] = result

        # 유효성 검사
        processed = [ext for ext in extensions if ext and ext not in ("error", None)]
        invalid = set(processed) - ALLOWED_EXTENSIONS

        if invalid:
            logging.error(f"[helper.llm.get_image_extension] Invalid extensions detected: {invalid}")
            raise ProxyServerError()

    return extensions
