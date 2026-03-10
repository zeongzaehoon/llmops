from __future__ import annotations

import os
import json
import base64
import logging
import asyncio
from uuid import uuid4
from dataclasses import dataclass, field
from typing import AsyncGenerator, Generator, Union
from contextlib import asynccontextmanager, contextmanager

import httpx
import numpy as np

from utils.error import LLMProxyError, LLMStreamingError
from utils.constants import EMBEDDING_MODEL



# dataclass
@dataclass
class GroxyArgs:
    """
    Role:
        - 동기 인스턴스(LLMProxyClient)의 커넥션 관련 데이터 클래스

    Args:
        - connection_name: str = "stream"
        - max_connections: int = 50
        - max_keepalive_connections: int = 15
        - keepalive_expiry: float = 30.0
        - connect_timeout: float = 5.0
        - read_timeout: float = 120.0
        - write_timeout: float = 10.0
        - pool_timeout: float = 5.0
    """
    connection_name: str = field(default="stream")
    # limits
    max_connections: int = field(default=50)
    max_keepalive_connections: int = field(default=15)
    keepalive_expiry: float = field(default=30.0)
    # timeout
    connect_timeout: float = field(default=5.0)
    read_timeout: float = field(default=120.0)
    write_timeout: float = field(default=10.0)
    pool_timeout: float = field(default=5.0)

@dataclass
class AsyncGroxyArgs(GroxyArgs):
    """
    Role:
        - 비동기 인스턴스(AsyncLLMProxyClient)의 커넥션 관련 데이터 클래스

    Args:
        - connection_name: str = "stream"
        - max_connections: int = 50
        - max_keepalive_connections: int = 15
        - keepalive_expiry: float = 30.0
        - connect_timeout: float = 5.0
        - read_timeout: float = 120.0
        - write_timeout: float = 10.0
        - pool_timeout: float = 5.0
        - semaphore: int = 30
    """
    semaphore: int = field(default=30)

@dataclass
class GroxyResponse:
    """
    Role:
        - chat의 response 객체

    Args:
        - text: str = None
        - vendor: str = None
        - model: str = None
        - tool_name: str = None
        - tool_text: str = None
        - thinking: str = None
        - is_end: bool = False
        - is_error: bool = False
        - assistant_content: str = None
        - tool_results: str = None

    Methods:
        - to_dict: Transform data to dictionary
    """
    text: Union[str, None] = field(default=None)
    vendor: Union[str, None] = field(default=None)
    model: Union[str, None] = field(default=None)
    tool_name: Union[str, None] = field(default=None)
    tool_text: Union[str, None] = field(default=None)
    thinking: Union[str, None] = field(default=None)
    is_end: bool = field(default=False)
    is_error: bool = field(default=False)
    assistant_content: Union[str, None] = field(default=None)
    tool_results: Union[str, None] = field(default=None)

    def to_dict(self):
        """
        Return:
            {
                "text": "",
                "vendor": "",
                "model": "",
                "tool_name": "",
                "tool_text": "",
                "thinking": "",
                "is_end": True | False,
                "is_error": True | False,
                "assistant_content": "",
                "tool_results": "",
            }
        """

        return {
            "text": self.text,
            "vendor": self.vendor,
            "model": self.model,
            "tool_name": self.tool_name,
            "tool_text": self.tool_text,
            "thinking": self.thinking,
            "is_end": self.is_end,
            "is_error": self.is_error,
            "assistant_content": self.assistant_content,
            "tool_results": self.tool_results,
        }

@dataclass
class GroxyStreamingResponse(GroxyResponse):
    """
    Role:
        - stream, stream_with_mcp의 response 객체

    Args:
        - iteration: int = 0
        - text: str = None
        - vendor: str = None
        - model: str = None
        - tool_name: str = None
        - tool_text: str = None
        - thinking: str = None
        - is_end: bool = False
        - is_error: bool = False
        - assistant_content: str = None
        - tool_results: str = None

    Methods:
        - to_dict: Transform data to dictionary
    """
    iteration: int = field(default=0)

    def to_dict(self):
        """
        Return:
        {
            "iteration": 0,
            "text": "",
            "vendor": "",
            "model": "",
            "tool_name": "",
            "tool_text": "",
            "thinking": "",
            "is_end": True | False,
            "is_error": True | False,
            "assistant_content": "",
            "tool_results": "",
        }
        """
        result:dict = super().to_dict()
        result["iteration"] = self.iteration
        return result



# client
@dataclass
class AsyncLLMProxyClient:
    """
    Role:
        -  비동기 application용 llm-proxy client

    Args:
        - uri: str = None
        - host: str = None
        - port: int = None
        - path: str = None
        - ssl: bool = False
            + False -> set scheme http
            + True -> set scheme https
        - args: AsyncGroxyArgs or dict = None

    Explain:
        - Must input [uri] or [host, ssl (+port, path)]
        - If not input args, use AsyncGroxyArgs with default value.
    """

    uri: str = field(default=None)
    host: str = field(default=None)
    port: int = field(default=None)
    path: str = field(default=None)
    ssl: bool = field(default=False)
    args: Union[AsyncGroxyArgs, dict] = field(default=None)

    _base_url = None
    _clients = {}
    _config = {}
    _default_headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    _lock = asyncio.Lock()


    def __post_init__(self):
        if self.args is None:
            self.args = AsyncGroxyArgs()
        self._set_base_url()
        self._set_config(args=self.args)

    def _set_base_url(self):
        if self.uri:
            self._base_url = self.uri.rstrip("/") + "/"
        elif self.host:
            scheme = "https" if self.ssl else "http"
            port = f":{self.port}" if self.port else ""
            path = f"{self.path}/" if self.path else ""
            self._base_url = f"{scheme}://{self.host}{port}/{path}"
        else:
            self._base_url = os.getenv("LLM_PROXY_URL")

    def _set_config(self, args: Union[AsyncGroxyArgs, dict] = None):
        if not args:
            args = AsyncGroxyArgs()
        if isinstance(args, dict):
            args = AsyncGroxyArgs(**args)

        if not args.connection_name in self._clients and not args.connection_name in self._config:
            max_connections = args.max_connections
            max_keepalive_connections = args.max_keepalive_connections
            keepalive_expiry = args.keepalive_expiry
            connect_timeout = args.connect_timeout
            read_timeout = args.read_timeout
            write_timeout = args.write_timeout
            pool_timeout = args.pool_timeout
            semaphore = args.semaphore

            self._config[args.connection_name] = {
                "limits": httpx.Limits(
                    max_connections=max_connections,
                    max_keepalive_connections=max_keepalive_connections,
                    keepalive_expiry=keepalive_expiry
                ),
                "timeout": httpx.Timeout(
                    connect=connect_timeout,
                    read=read_timeout,
                    write=write_timeout,
                    pool=pool_timeout
                ),
                "semaphore": asyncio.Semaphore(semaphore)
            }


    async def connect(self):
        """
        Role:
            - 인스턴스 내 커넥션 생성
            - 인스턴스 선언할 때 입력했던 args.connection_name(args['connection_name'])을 이름으로 한 커넥션을 생성한다.
            - args를 주지 않으면 stream 이란 이름으로 커넥션이 생성된다.
        """
        if self._clients.get(self.args.connection_name) is None or (isinstance(self.args.connection_name, httpx.AsyncClient) and self._clients[self.args.connection_name].is_closed):
            self._clients[self.args.connection_name] = httpx.AsyncClient(
                limits=self._config[self.args.connection_name]["limits"],
                timeout=self._config[self.args.connection_name]["timeout"],
                headers=self._default_headers
            )
        logging.info(f"[groxy.AsyncLLMProxyClient.connect] ✅ Successfully connect to LLM Proxy Client: {self.args.connection_name}")


    async def disconnect(self, connection_name: str = None):
        """
        Role:
            - 인스턴스 내 커넥션 끊음
            - connection_name을 지정하면 지정한 이름의 커넥션만 끊음
            - connection_name을 주지 않으면 인스턴스 내 생성된 모든 커넥션을 끊음

        Args:
            - connection_name: str = None
        """
        if connection_name:
            if self._clients.get(connection_name) and isinstance(self._clients[connection_name], httpx.AsyncClient) and not self._clients[connection_name].is_closed:
                await self._clients[connection_name].aclose()
            self._clients[connection_name] = None
        else:
            self._base_url = None
            for client_name_each, client in self._clients.items():
                if client and isinstance(client, httpx.AsyncClient) and not client.is_closed:
                    await client.aclose()
                self._clients[client_name_each] = None
        logging.info(f"[groxy.AsyncLLMProxyClient.disconnect] 🔴 Disconnected LLM Proxy Client: {'ALL' if not connection_name else connection_name}")


    async def add_connection(self, connection_name: str = None, args: Union[AsyncGroxyArgs, dict] = None):
        """
        Role:
            - 인스턴스 내 커넥션 추가 생성
            - 'connection_name'을 지정하면 지정한 이름으로 커넥션 추가 생성
            - 'connection_name'을 지정해주지 않으면 embedding 이란 이름으로 커넥션 추가 생성

        Args:
            - connection_name: str = None
            - args: Union[AsyncGroxyArgs, dict]
        """
        if not connection_name:
            connection_name = "embedding"

        if not args:
            args = AsyncGroxyArgs(connection_name=connection_name)
        if isinstance(args, dict):
            args = AsyncGroxyArgs(**args)
        if getattr(args, "connection_name", None) == "stream":
            args.connection_name = connection_name

        if args.connection_name not in self._clients:
            self._set_config(args=args)
            self._clients[args.connection_name] = httpx.AsyncClient(limits=self._config[args.connection_name]["limits"], timeout=self._config[args.connection_name]["timeout"], headers=self._default_headers)
            logging.info(f"[groxy.AsyncLLMProxyClient.add_connection] ✅ Successfully add connection: {args.connection_name}")


    async def _ensure_client(self, connection_name: str):
        if self._clients.get(connection_name) is None or (isinstance(self._clients[connection_name], httpx.AsyncClient) and self._clients[connection_name].is_closed):
            if not connection_name in self._config:
                self._set_config(AsyncGroxyArgs(connection_name=connection_name))

            async with self._lock:
                self._clients[connection_name] = httpx.AsyncClient(limits=self._config[connection_name]["limits"], timeout=self._config[connection_name]["timeout"], headers=self._default_headers)


    @asynccontextmanager
    async def _get_client(self, connection_name: str) -> AsyncGenerator[httpx.AsyncClient, None]:
        await self._ensure_client(connection_name)
        try:
            yield self._clients[connection_name]
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            logging.warning(f"[groxy.AsyncLLMProxyClient._get_client] 🔴 Connection Error. Try reconnect")
            await self.disconnect(connection_name)
            await self._ensure_client(connection_name)
            yield self._clients[connection_name]
            logging.info(f"[groxy.AsyncLLMProxyClient._get_client] ✅ Successfully yield client while reconnecting")


    async def stream(
            self,
            service: str,
            vendor: str,
            model: str,
            system_message: str = None,
            system_message_placeholder: dict = None,
            conversation_history: list = None,
            human_message: Union[str, None] = None,
            images: list = None, # images: Optional[list] = Field([], description="max: 20 images")
            image_types: list = None, # image_types: Optional[list] = Field([], alias="imageTypes", description="only base64 or url")
            image_filename_extensions: list = None, # image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
            temperature: float = None,
            time:float = None,
            store_name: str = None,
            connection_name: str = None,
            session_key: str = None
    ):
        """
        Role:
            - LLM에 스트리밍 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            responses = [GroxyStreamingResponse(...), GroxyStreamingResponse(...), GroxyStreamingResponse(...), ...]
            async for response in responses:
                yield response
            ```
        """
        try:
            connection_name = connection_name or 'stream'
            payload = {
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            await self._ensure_client(connection_name)
            async with self._config[connection_name]["semaphore"]:
                # noinspection PyArgumentList
                async with self._get_client(connection_name=connection_name) as client:
                    async with client.stream(method="POST", url=self._base_url+"llm/chat", headers=self._default_headers, json=payload) as response:
                        response.raise_for_status()
                        full_dict = str()
                        async for chunk in response.aiter_lines():
                            if chunk:
                                full_dict += chunk
                                if chunk.endswith("}"):
                                    try:
                                        response_dict = json.loads(full_dict)
                                        response_object = GroxyStreamingResponse(
                                            iteration=response_dict.get("iteration", 0),
                                            text=response_dict.get("text"),
                                            vendor=response_dict.get("vendor"),
                                            model=response_dict.get("model"),
                                            tool_name=response_dict.get("tool_name"),
                                            tool_text=response_dict.get("tool_text"),
                                            thinking=response_dict.get("thinking"),
                                            is_end=response_dict.get("is_end", False),
                                            is_error=response_dict.get("is_error", False),
                                            assistant_content=response_dict.get("assistant_content"),
                                            tool_results=response_dict.get("tool_results")
                                        )
                                        yield response_object
                                        full_dict = str()
                                    except json.JSONDecodeError:
                                        continue

        except Exception as e:
            logging.info(f"[groxy.AsyncLLMProxyClient.stream] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMStreamingError(f"Failed to send request to Proxy Server: {e}")


    async def stream_with_mcp(
            self,
            service: str,
            vendor: str,
            model: str,
            mcp_info: list[dict] = None,
            mcp_server: str = None,
            mcp_token: str = None,
            mcp_allowed_tools: Union[list, None] = None,
            system_message: str = None,
            system_message_placeholder: dict = None,
            conversation_history: list = None,
            human_message: Union[str, None] = None,
            images: list = None, # images: Optional[list] = Field([], description="max: 20 images")
            image_types: list = None, # image_types: Optional[list] = Field([], alias="imageTypes", description="only base64 or url")
            image_filename_extensions: list = None, # image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
            temperature: float = None,
            time:float = None,
            store_name: str = None,
            connection_name: str = None,
            session_key: str = None
    ):
        """
        Role:
            - MCP 서버를 활용한 LLM 스트리밍 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - mcp_info (list[dict]): MCP 서버 정보 리스트
            - mcp_server (str): MCP 서버 주소 (mcp_info 미사용 시)
            - mcp_token (str): MCP 서버 토큰 (mcp_info 미사용 시)
            - mcp_allowed_tools (list): MCP 허용 툴 리스트 (mcp_info 미사용 시)
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            responses = [GroxyStreamingResponse(...), GroxyStreamingResponse(...), GroxyStreamingResponse(...), ...]
            async for response in responses:
                yield response
            ```
        """
        try:
            connection_name = connection_name or 'stream'
            payload = {
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if mcp_info:
                payload["mcpInfo"] = mcp_info
            else:
                if not all([mcp_server, mcp_token, mcp_allowed_tools]):
                    raise ValueError("mcp_server, mcp_token, mcp_allowed_tools are required if mcp_info is not provided")
                payload["mcpServer"] = mcp_server
                payload["mcpToken"] = mcp_token
                payload["mcpAllowedTools"] = mcp_allowed_tools
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            # async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            await self._ensure_client(connection_name)
            async with self._config[connection_name]["semaphore"]:
                # noinspection PyArgumentList
                async with self._get_client(connection_name=connection_name) as client:
                    async with client.stream(method="POST", url=self._base_url+"llm/chat_mcp", headers=self._default_headers, json=payload) as response:
                        response.raise_for_status()
                        full_dict = str()
                        async for chunk in response.aiter_lines():
                            if chunk:
                                full_dict += chunk
                                if chunk.endswith("}"):
                                    try:
                                        response_dict = json.loads(full_dict)
                                        response_object = GroxyStreamingResponse(
                                            iteration=response_dict.get("iteration", 0),
                                            text=response_dict.get("text"),
                                            vendor=response_dict.get("vendor"),
                                            model=response_dict.get("model"),
                                            tool_name=response_dict.get("tool_name"),
                                            tool_text=response_dict.get("tool_text"),
                                            thinking=response_dict.get("thinking"),
                                            is_end=response_dict.get("is_end", False),
                                            is_error=response_dict.get("is_error", False),
                                            assistant_content=response_dict.get("assistant_content"),
                                            tool_results=response_dict.get("tool_results")
                                        )
                                        yield response_object
                                        full_dict = str()
                                    except json.JSONDecodeError:
                                        continue

        except Exception as e:
            logging.info(f"[groxy.AsyncLLMProxyClient.stream_with_mcp] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMStreamingError(f"Failed to send request to Proxy Server: {e}")


    async def chat(
            self,
            service: str,
            vendor: str,
            model: str,
            system_message: str = None,
            system_message_placeholder: dict = None,
            conversation_history: list = None,
            human_message: Union[str, None] = None,
            images: list = None,
            image_types: list = None,
            image_filename_extensions: list = None,
            temperature: float = None,
            time:float = None,
            store_name: str = None,
            connection_name: str = None,
            session_key: str = None
    ):
        """
        Role:
            - LLM에 전체 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            return GroxyResponse(...)
            ```
        """

        try:
            connection_name = connection_name or 'stream'
            payload = {
                "stream": False,
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            # noinspection PyArgumentList
            async with self._get_client(connection_name=connection_name) as client:
                response = await client.post(url=self._base_url+"llm/chat", headers=self._default_headers, json=payload)
                response.raise_for_status()
                response_dict = response.json()
                response_object = GroxyResponse(
                    vendor=response_dict.get("vendor", vendor),
                    model=response_dict.get("model", model),
                    text=response_dict.get("text"),
                    thinking=response_dict.get("thinking"),
                    is_end=response_dict.get("is_end", False),
                    is_error=response_dict.get("is_error", False),
                )
                return response_object

        except Exception as e:
            logging.error(f"[groxy.AsyncLLMProxyClient.chat] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    # async def chat_with_mcp(
    #         self,
    #         service: str,
    #         vendor: str,
    #         model: str,
    #         mcp_info: list[dict] = None,
    #         mcp_server: str = None,
    #         mcp_token: str = None,
    #         mcp_allowed_tools: Union[list, None] = None,
    #         system_message: str = None,
    #         system_message_placeholder: dict = None,
    #         conversation_history: list = None,
    #         human_message: Union[str, None] = None,
    #         images: list = None,
    #         image_types: list = None,
    #         image_filename_extensions: list = None,
    #         temperature: float = None,
    #         time:float = None,
    #         store_name: str = None,
    #         connection_name: str = None,
    #         session_key: str = None
    # ):
    #     try:
    #         connection_name = connection_name or 'stream'
    #         payload = {
    #             "stream": False,
    #             "service": service,
    #             "vendor": vendor,
    #             "model": model,
    #             "systemMessage": system_message or "",
    #             "systemMessagePlaceholder": system_message_placeholder or {},
    #             "conversationHistory": conversation_history or [],
    #             "question": human_message or "",
    #             "images": images or [],
    #             "imageTypes": image_types or [],
    #             "imageFilenameExtensions": image_filename_extensions or [],
    #             "temperature": temperature or 0.2
    #         }
    #         if mcp_info:
    #             payload["mcpInfo"] = mcp_info
    #         else:
    #             if not all([mcp_server, mcp_token, mcp_allowed_tools]):
    #                 raise ValueError("mcp_server, mcp_token, mcp_allowed_tools are required if mcp_info is not provided")
    #             payload["mcpServer"] = mcp_server
    #             payload["mcpToken"] = mcp_token
    #             payload["mcpAllowedTools"] = mcp_allowed_tools
    #         if time:
    #             payload["time"] = time
    #         if store_name:
    #             payload["storeName"] = store_name
    #         if session_key:
    #             payload["sessionKey"] = session_key
    #
    #         async with self._get_client(connection_name) as client:
    #             response = await client.post(url=self._base_url+"llm/chat_mcp", headers=self._default_headers, json=payload)
    #             response.raise_for_status()
    #             response_dict = response.json()
    #             return GroxyResponse(
    #                 text=response_dict.get("text"),
    #                 vendor=response_dict.get("vendor", vendor),
    #                 model=response_dict.get("model", model),
    #                 tool_name=response_dict.get("tool_name"),
    #                 tool_text=response_dict.get("tool_text"),
    #                 thinking=response_dict.get("thinking"),
    #                 is_end=response_dict.get("is_end", False),
    #                 is_error=response_dict.get("is_error", False),
    #                 assistant_content=response_dict.get("assistant_content"),
    #                 tool_results=response_dict.get("tool_results")
    #             )
    #
    #     except Exception as e:
    #         logging.error(f"[groxy.AsyncLLMProxyClient.chat_with_mcp] 🔴 Failed to send request to Proxy Server: {e}")
    #         raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    async def embeddings(
            self,
            text: Union[str, list[str]],
            service: str,
            connection_name: str = None
    ):
        """
        Role:
            - vectorDB 사용하기 위한 text -> vector 변경 요청

        Args:
            - text (str | list[str]): 변경할 텍스트
            - service (str): 서비스 식별자
            - connection_name (str): 커넥션 이름. Defaults to "embedding".

        Return:
            - text가 str이면 list[float]
            - text가 list[str]이면 list[list[float]]
        """
        connection_name = connection_name or 'embedding'
        try:
            payload = {
                "service": service,
                "model": EMBEDDING_MODEL,
                "text": text,
                "debugId": str(uuid4())[:8]
            }
            logging.info(f"[groxy.AsyncLLMProxyClient.embeddings] debugId: {payload['debugId']}")
            await self._ensure_client(connection_name)
            async with self._config[connection_name]["semaphore"]:
                # noinspection PyArgumentList
                async with self._get_client(connection_name=connection_name) as client:
                    response = await client.post(url=self._base_url+"llm/embeddings", headers=self._default_headers, json=payload)
                    response.raise_for_status()
                    response_dict = response.json()
                    vectors = response_dict.get("vectors")
                    debug_id = response_dict.get("debugId")
                    logging.info(f"[groxy.AsyncLLMProxyClient.embeddings] debugId: {debug_id}")

                    if isinstance(vectors, list):
                        result = []
                        for base64_vector in vectors:
                            decoded_vector = base64.b64decode(base64_vector)
                            vector = np.frombuffer(decoded_vector, dtype=np.float32)
                            result.append(vector.tolist())
                    else:
                        decoded_vector = base64.b64decode(vectors)
                        vector = np.frombuffer(decoded_vector, dtype=np.float32)
                        result = vector.tolist()
                    return result
        except Exception as e:
            logging.info(f"[groxy.AsyncLLMProxyClient.embeddings] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")



@dataclass
class LLMProxyClient:
    """
    Role:
    -  동기 application용 llm-proxy client

    Args:
        - uri: str = None
        - host: str = None
        - port: int = None
        - path: str = None
        - ssl: bool = False
            + False -> set scheme http
            + True -> set scheme https
        - args: GroxyArgs or dict = None

    Explain:
        - Must input [uri] or [host, ssl (+port, path)]
        - If not input args, use GroxyArgs with default value.
    """

    uri: str = None
    host: str = None
    port: int = None
    path: str = None
    ssl: bool = False
    args: Union[GroxyArgs, dict] = None

    _base_url = None
    _clients = {}
    _config = {}
    _default_headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }


    def __post_init__(self):
        if self.args is None:
            self.args = GroxyArgs()
        self._set_base_url()
        self._set_config(args=self.args)


    def _set_base_url(self):
        if self.uri:
            self._base_url = self.uri.rstrip("/") + "/"
        elif self.host:
            scheme = "https" if self.ssl else "http"
            port = f":{self.port}" if self.port else ""
            path = f"{self.path}/" if self.path else ""
            self._base_url = f"{scheme}://{self.host}{port}/{path}"
        else:
            self._base_url = os.getenv("LLM_PROXY_URL")


    def _set_config(self, args: Union[GroxyArgs, dict] = None):
        if not args:
            args = GroxyArgs()
        elif isinstance(args, dict):
            args = GroxyArgs(**args)

        if not args.connection_name in self._clients and not args.connection_name in self._config:
            max_connections = args.max_connections
            max_keepalive_connections = args.max_keepalive_connections
            keepalive_expiry = args.keepalive_expiry
            connect_timeout = args.connect_timeout
            read_timeout = args.read_timeout
            write_timeout = args.write_timeout
            pool_timeout = args.pool_timeout

            self._config[args.connection_name] = {
                "limits": httpx.Limits(
                    max_connections=max_connections,
                    max_keepalive_connections=max_keepalive_connections,
                    keepalive_expiry=keepalive_expiry
                ),
                "timeout": httpx.Timeout(
                    connect=connect_timeout,
                    read=read_timeout,
                    write=write_timeout,
                    pool=pool_timeout
                )
            }


    def connect(self):
        """
        Role:
            - 인스턴스 내 커넥션 생성
            - 인스턴스 선언할 때 입력했던 args.connection_name(args['connection_name'])을 이름으로 한 커넥션을 생성한다.
            - args를 주지 않으면 stream 이란 이름으로 커넥션이 생성된다.
        """
        if self._clients.get(self.args.connection_name) is None or (isinstance(self._clients[self.args.connection_name], httpx.Client) and self._clients[self.args.connection_name].is_closed):
            self._clients[self.args.connection_name] = httpx.Client(
                limits=self._config[self.args.connection_name]["limits"],
                timeout=self._config[self.args.connection_name]["timeout"],
                headers=self._default_headers
            )
        logging.info(f"[groxy.LLMProxyClient.connect] ✅ Successfully connect to LLM Proxy Client: {self.args.connection_name}")


    def disconnect(self, connection_name: str = None):
        """
        Role:
            - 인스턴스 내 커넥션 끊음
            - connection_name을 지정하면 지정한 이름의 커넥션만 끊음
            - connection_name을 주지 않으면 인스턴스 내 생성된 모든 커넥션을 끊음

        Args:
            - connection_name: str = None
        """
        if connection_name:
            if self._clients.get(connection_name) and isinstance(self._clients[connection_name], httpx.Client) and not self._clients[connection_name].is_closed:
                self._clients[connection_name].close()
            self._clients[connection_name] = None
        else:
            for client_name_each, client in self._clients.items():
                if client and isinstance(client, httpx.Client) and not client.is_closed:
                    client.close()
                self._clients[client_name_each] = None
        logging.info(f"[groxy.LLMProxyClient.disconnect] 🔴 Disconnected LLM Proxy Client: {'ALL' if not connection_name else connection_name}")


    def add_connection(self, connection_name:str = None, args: Union[GroxyArgs, dict] = None):
        """
        Role:
            - 인스턴스 내 커넥션 추가 생성
            - 'connection_name'을 지정하면 지정한 이름으로 커넥션 추가 생성
            - 'connection_name'을 지정해주지 않으면 embedding 이란 이름으로 커넥션 추가 생성

        Args:
            - connection_name: str = None
            - args: Union[GroxyArgs, dict]
        """
        if not connection_name:
            connection_name = "embedding"

        if not args:
            args = GroxyArgs(connection_name=connection_name)
        if isinstance(args, dict):
            args = GroxyArgs(**args)
        if getattr(args, "connection_name", None) == "stream":
            args.connection_name = connection_name

        if not args.connection_name in self._clients:
            self._set_config(args=args)
            self._clients[args.connection_name] = httpx.Client(limits=self._config[args.connection_name]["limits"], timeout=self._config[args.connection_name]["timeout"], headers=self._default_headers)

        logging.info(f"[groxy.LLMProxyClient.add_connection] ✅ Successfully add connection: {args.connection_name}")


    def _ensure_client(self, connection_name: str):
        if self._clients.get(connection_name) is None or (isinstance(self._clients[connection_name], httpx.Client) and self._clients[connection_name].is_closed):
            if self._config.get(connection_name) is None:
                self._set_config(GroxyArgs(connection_name=connection_name))

            self._clients[connection_name] = httpx.Client(limits=self._config[connection_name]["limits"], timeout=self._config[connection_name]["timeout"], headers=self._default_headers)
            logging.info(f"[groxy.LLMProxyClient.add_connection] ✅ Successfully add connection: {connection_name}")


    @contextmanager
    def get_client(self, connection_name: str = None) -> Generator[httpx.Client, None, None]:
        connection_name = connection_name or self.args.connection_name
        self._ensure_client(connection_name=connection_name)
        try:
            yield self._clients[connection_name]
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            logging.warning(f"[groxy.LLMProxyClient.get_client] 🔴 Connection Error. Try reconnect: {e}")
            self.disconnect(connection_name)
            self._ensure_client(connection_name)
            yield self._clients[connection_name]
            logging.info(f"[groxy.LLMProxyClient.get_client] ✅ Successfully yield client while reconnecting")


    def stream(
        self,
        service: str,
        vendor: str,
        model: str,
        system_message: str = None,
        system_message_placeholder: dict = None,
        conversation_history: list = None,
        human_message: Union[str, None] = None,
        images: list = None, # images: Optional[list] = Field([], description="max: 20 images")
        image_types: list = None, # image_types: Optional[list] = Field([], alias="imageTypes", description="only base64 or url")
        image_filename_extensions: list = None, # image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
        temperature: float = None,
        time:float = None,
        store_name: str = None,
        connection_name: str = None,
        session_key: str = None
    ):
        """
        Role:
            - LLM에 스트리밍 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            responses = [GroxyStreamingResponse(...), GroxyStreamingResponse(...), GroxyStreamingResponse(...), ...]
            for response in responses:
                yield response
            ```
        """

        try:
            connection_name = connection_name or 'stream'
            payload = {
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            # noinspection PyArgumentList
            with self.get_client(connection_name=connection_name) as client:
                response = client.post(url=self._base_url+"llm/chat", headers=self._default_headers, json=payload)
                response.raise_for_status()
                full_dict = ""
                for chunk in response.iter_lines():
                    if chunk and chunk.endswith("}"):
                        try:
                            full_dict += chunk
                            if not full_dict.strip():
                                full_dict = ""
                                continue
                            response_dict = json.loads(full_dict)
                            response_object = GroxyStreamingResponse(
                                iteration=response_dict.get("iteration", 0),
                                text=response_dict.get("text"),
                                vendor=response_dict.get("vendor"),
                                model=response_dict.get("model"),
                                tool_name=response_dict.get("tool_name"),
                                tool_text=response_dict.get("tool_text"),
                                thinking=response_dict.get("thinking"),
                                is_end=response_dict.get("is_end", False),
                                is_error=response_dict.get("is_error", False),
                                assistant_content=response_dict.get("assistant_content"),
                                tool_results=response_dict.get("tool_results")
                            )
                            yield response_object
                            full_dict = str()
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.error(f"[groxy.LLMProxyClient.stream] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    def stream_with_mcp(
            self,
            service: str,
            vendor: str,
            model: str,
            mcp_info: list[dict] = None,
            mcp_server: str = None,
            mcp_token: str = None,
            mcp_allowed_tools: Union[list, None] = None,
            system_message: str = None,
            system_message_placeholder: dict = None,
            conversation_history: list = None,
            human_message: Union[str, None] = None,
            images: list = None, # images: Optional[list] = Field([], description="max: 20 images")
            image_types: list = None, # image_types: Optional[list] = Field([], alias="imageTypes", description="only base64 or url")
            image_filename_extensions: list = None, # image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
            temperature: float = None,
            time:float = None,
            store_name: str = None,
            connection_name: str = None,
            session_key: str = None
    ):
        """
        Role:
            - MCP 서버를 활용한 LLM 스트리밍 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - mcp_info (list[dict]): MCP 서버 정보 리스트
            - mcp_server (str): MCP 서버 주소 (mcp_info 미사용 시)
            - mcp_token (str): MCP 서버 토큰 (mcp_info 미사용 시)
            - mcp_allowed_tools (list): MCP 허용 툴 리스트 (mcp_info 미사용 시)
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            responses = [GroxyStreamingResponse(...), GroxyStreamingResponse(...), GroxyStreamingResponse(...), ...]
            for response in responses:
                yield response
            ```
        """

        try:
            payload = {
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if mcp_info:
                payload["mcpInfo"] = mcp_info
            else:
                if not all([mcp_server, mcp_token, mcp_allowed_tools]):
                    raise ValueError("mcp_server, mcp_token, mcp_allowed_tools are required if mcp_info is not provided")
                payload["mcpServer"] = mcp_server
                payload["mcpToken"] = mcp_token
                payload["mcpAllowedTools"] = mcp_allowed_tools
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            connection_name = connection_name or 'stream'

            # noinspection PyArgumentList
            with self.get_client(connection_name=connection_name) as client:
                response = client.post(url=self._base_url+"llm/chat_mcp", headers=self._default_headers, json=payload)
                response.raise_for_status()
                full_dict = str()
                for chunk in response.iter_lines():
                    if chunk and chunk.endswith("}"):
                        full_dict += chunk
                        if not full_dict.strip():
                            full_dict = ""
                            continue
                        try:
                            response_dict = json.loads(full_dict)
                            response_object = GroxyStreamingResponse(
                                iteration=response_dict.get("iteration", 0),
                                text=response_dict.get("text"),
                                vendor=response_dict.get("vendor"),
                                model=response_dict.get("model"),
                                tool_name=response_dict.get("tool_name"),
                                tool_text=response_dict.get("tool_text"),
                                thinking=response_dict.get("thinking"),
                                is_end=response_dict.get("is_end", False),
                                is_error=response_dict.get("is_error", False),
                                assistant_content=response_dict.get("assistant_content"),
                                tool_results=response_dict.get("tool_results")
                            )
                            yield response_object
                            full_dict = str()
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logging.info(f"[groxy.LLMProxyClient.stream_with_mcp] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    def chat(
        self,
        service: str,
        vendor: str,
        model: str,
        system_message: str = None,
        system_message_placeholder: dict = None,
        conversation_history: list = None,
        human_message: Union[str, None] = None,
        images: list = None,
        image_types: list = None,
        image_filename_extensions: list = None,
        temperature: float = None,
        time: float = None,
        store_name: str = None,
        connection_name: str = None,
        session_key: str = None
    ):
        """
        Role:
            - LLM에 전체 답변 요청

        Args:
            - service (str): 서비스 식별자
            - vendor (str): LLM 공급사 (openai, anthropic, bedrock 등)
            - model (str): 모델 ID
            - system_message (str): 시스템 메세지
            - system_message_placeholder (dict): 시스템 프롬프트 플레이스홀더
            - conversation_history (list): 대화 이력
            - human_message (str): 사용자 메세지
            - images (list): 이미지 데이터 (url 또는 base64)
            - image_types (list): 이미지 타입 (url 또는 base64)
            - image_filename_extensions (list): 이미지 확장명
            - temperature (float): 답변 감성 정도. Defaults to 0.2.
            - time (float): 성능 체크용 시간 값
            - store_name (str): gemini filesearch-api RAG용
            - connection_name (str): 커넥션 이름. Defaults to "stream".
            - session_key (str): 세션 구분용 키

        Return:
            ```python
            return GroxyResponse(...)
            ```
        """

        try:
            connection_name = connection_name or 'stream'
            payload = {
                "stream": False,
                "service": service,
                "vendor": vendor,
                "model": model,
                "systemMessage": system_message or "",
                "systemMessagePlaceholder": system_message_placeholder or {},
                "conversationHistory": conversation_history or [],
                "question": human_message or "",
                "images": images or [],
                "imageTypes": image_types or [],
                "imageFilenameExtensions": image_filename_extensions or [],
                "temperature": temperature or 0.2
            }
            if time:
                payload["time"] = time
            if store_name:
                payload["storeName"] = store_name
            if session_key:
                payload["sessionKey"] = session_key

            # noinspection PyArgumentList
            with self.get_client(connection_name=connection_name) as client:
                response = client.post(url=self._base_url+"llm/chat", headers=self._default_headers, json=payload)
                response.raise_for_status()
                response_dict = response.json()
                response_object = GroxyResponse(
                    vendor=response_dict.get("vendor", vendor),
                    model=response_dict.get("model", model),
                    text=response_dict.get("text"),
                    thinking=response_dict.get("thinking"),
                    is_end=response_dict.get("is_end", False),
                    is_error=response_dict.get("is_error", False)
                )
                return response_object

        except Exception as e:
            logging.error(f"[groxy.LLMProxyClient.chat] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    # def chat_with_mcp(
    #         self,
    #         service: str,
    #         vendor: str,
    #         model: str,
    #         mcp_info: list[dict] = None,
    #         mcp_server: str = None,
    #         mcp_token: str = None,
    #         mcp_allowed_tools: Union[list, None] = None,
    #         system_message: str = None,
    #         system_message_placeholder: dict = None,
    #         conversation_history: list = None,
    #         human_message: Union[str, None] = None,
    #         images: list = None,
    #         image_types: list = None,
    #         image_filename_extensions: list = None,
    #         temperature: float = None,
    #         time: float = None,
    #         store_name: str = None,
    #         connection_name: str = None,
    #         session_key: str = None
    # ):
    #     try:
    #         connection_name = connection_name or 'stream'
    #         payload = {
    #             "stream": False,
    #             "service": service,
    #             "vendor": vendor,
    #             "model": model,
    #             "systemMessage": system_message or "",
    #             "systemMessagePlaceholder": system_message_placeholder or {},
    #             "conversationHistory": conversation_history or [],
    #             "question": human_message or "",
    #             "images": images or [],
    #             "imageTypes": image_types or [],
    #             "imageFilenameExtensions": image_filename_extensions or [],
    #             "temperature": temperature or 0.2
    #         }
    #         if mcp_info:
    #             payload["mcpInfo"] = mcp_info
    #         else:
    #             if not all([mcp_server, mcp_token, mcp_allowed_tools]):
    #                 raise ValueError("mcp_server, mcp_token, mcp_allowed_tools are required if mcp_info is not provided")
    #             payload["mcpServer"] = mcp_server
    #             payload["mcpToken"] = mcp_token
    #             payload["mcpAllowedTools"] = mcp_allowed_tools
    #         if time:
    #             payload["time"] = time
    #         if store_name:
    #             payload["storeName"] = store_name
    #         if session_key:
    #             payload["sessionKey"] = session_key
    #
    #         with self.get_client(connection_name) as client:
    #             response = client.post(url=self._base_url+"llm/chat_mcp", headers=self._default_headers, json=payload)
    #             response.raise_for_status()
    #             response_dict = response.json()
    #             return GroxyResponse(
    #                 text=response_dict.get("text"),
    #                 vendor=response_dict.get("vendor", vendor),
    #                 model=response_dict.get("model", model),
    #                 tool_name=response_dict.get("tool_name"),
    #                 tool_text=response_dict.get("tool_text"),
    #                 thinking=response_dict.get("thinking"),
    #                 is_end=response_dict.get("is_end", False),
    #                 is_error=response_dict.get("is_error", False),
    #                 assistant_content=response_dict.get("assistant_content"),
    #                 tool_results=response_dict.get("tool_results")
    #             )
    #
    #     except Exception as e:
    #         logging.error(f"[groxy.LLMProxyClient.chat_with_mcp] 🔴 Failed to send request to Proxy Server: {e}")
    #         raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")


    def embeddings(
        self,
        text: Union[str, list[str]],
        service: str,
        connection_name: str = None
    ):
        """
        Role:
            - vectorDB 사용하기 위한 text -> vector 변경 요청

        Args:
            - text (str | list[str]): 변경할 텍스트
            - service (str): 서비스 식별자
            - connection_name (str): 커넥션 이름. Defaults to "embedding".

        Return:
            - text가 str이면 list[float]
            - text가 list[str]이면 list[list[float]]
        """

        try:
            payload = {
                "model": EMBEDDING_MODEL,
                "text": text,
                "service": service
            }
            connection_name = connection_name or 'embedding'

            # noinspection PyArgumentList
            with self.get_client(connection_name=connection_name) as client:
                response = client.post(url=self._base_url+"llm/embeddings", headers=self._default_headers, json=payload)
                response.raise_for_status()
                response_json = response.json()
                if isinstance(response_json, list):
                    result = []
                    for base64_vector in response_json:
                        decoded_vector = base64.b64decode(base64_vector)
                        vector = np.frombuffer(decoded_vector, dtype=np.float32)
                        result.append(vector.tolist())  # numpy array를 list로 변환
                else:
                    # 단일 값 처리: base64 문자열을 직접 디코딩
                    decoded_vector = base64.b64decode(response_json)
                    vector = np.frombuffer(decoded_vector, dtype=np.float32)
                    result = vector.tolist()

                return result
        except Exception as e:
            logging.error(f"[client.llm_proxy.LLMProxyClient.embeddings] 🔴 Failed to send request to Proxy Server: {e}")
            raise LLMProxyError(f"Failed to send request to Proxy Server: {e}")
