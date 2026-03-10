import os
import json
import orjson
import logging
import asyncio
import base64
from datetime import timedelta
from time import time, sleep
from dataclasses import dataclass

import numpy as np

from utils.constants import *
from utils.error import *
from models.llm import *
from client.fastmcp import create_mcp_client


def detect_image_format(data: bytes) -> str | None:
    """imghdr 대체: magic bytes로 이미지 포맷 판별"""
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if data[:2] == b'\xff\xd8':
        return 'jpeg'
    if data[:4] == b'GIF8':
        return 'gif'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    if data[:4] in (b'II\x2a\x00', b'MM\x00\x2a'):
        return 'tiff'
    if data[:4] == b'\x00\x00\x01\x00':
        return 'ico'
    if data[:2] == b'BM':
        return 'bmp'
    return None



def make_response(iteration):
    return {
        # for common
        "iteration": iteration,
        "text": None,
        "model": None,
        "vendor": None,
        "tool_name": None,
        "tool_text": None,
        "thinking": None,
        "is_end": False,
        "is_error": False,

        # for backend
        "assistant_content": None,
        "tool_results": None
    }


def make_error_response(iteration=None):
    """에러 발생 시 클라이언트에 전달할 응답 생성"""
    iteration = iteration or 0

    response_dict = make_response(iteration=iteration)
    response_dict["is_end"] = True
    response_dict["is_error"] = True

    return serialize_response(response_dict)


def clean_surrogates(text:str|None):
    if text is None:
        return None
    return text.encode('utf-8', errors='ignore').decode('utf-8')


def serialize_response(response_dict: dict):
    if response_dict.get('text'):
        response_dict['text'] = clean_surrogates(response_dict['text'])
    return orjson.dumps(response_dict) + b"\n"


async def iter_with_first_text_timeout(vendor, response, instance=None, timeout=None, session_key=None):
    iterator = response.__aiter__()
    first_target_received = False
    start_time = time()
    timeout = timeout or 10
    instance_type = (OPENAI, ANTHROPIC, AZURE)
    instance_name = instance.__name__ if instance else "first streaming data"

    while True:
        try:
            if not first_target_received:
                elapsed = time() - start_time
                remaining = timeout - elapsed
                logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] elapsed: {elapsed:.2f}s, remaining: {remaining:.2f}s, waiting for: {instance_name}")
                if remaining <= 0:
                    logging.error(f"session_key: {session_key} | [iter_with_first_text_timeout] TIMEOUT: {timeout}s - no {instance_name} received")
                    raise asyncio.TimeoutError()
                chunk = await asyncio.wait_for(iterator.__anext__(), timeout=remaining)
                logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] got chunk: {type(chunk).__name__}")
            else:
                chunk = await iterator.__anext__()
        except StopAsyncIteration:
            logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] Stop Generating")
            if not first_target_received:
                logging.error(f"session_key: {session_key} | [iter_with_first_text_timeout] stream ended without {instance_name}")
                raise asyncio.TimeoutError(f"session_key: {session_key} | [iter_with_first_text_timeout] No {instance_name} received before stream ended")
            return
        except asyncio.TimeoutError:
            logging.error(f"session_key: {session_key} | [iter_with_first_text_timeout] TIMEOUT after {time() - start_time:.2f}s - no {instance_name} received")
            raise

        yield chunk


        if vendor in instance_type and not first_target_received and isinstance(chunk, instance):
            logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] first {instance_name} received after {time() - start_time:.2f}s")
            first_target_received = True
        if vendor == GOOGLE and not first_target_received and hasattr(chunk, 'candidates') and chunk.candidates:
            logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] first candidates received after {time() - start_time:.2f}s")
            first_target_received = True
        if vendor == BEDROCK and not first_target_received and chunk:
            bytes_data = chunk.get("chunk", {}).get("bytes", b"")
            if bytes_data:
                try:
                    data = json.loads(bytes_data.decode('utf-8'))
                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        if (delta.get("type") == "text_delta" and delta.get("text")) or (delta.get("type") == "thinking_delta" and delta.get("thinking")):
                            logging.info(f"session_key: {session_key} | [iter_with_first_text_timeout] first text_delta or thinking_delta received after {time() - start_time:.2f}s")
                            first_target_received = True
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
