import os
import logging
from dataclasses import dataclass
import asyncio
from contextlib import asynccontextmanager
import httpx



@dataclass
class SlackClient:
    _clients = None
    _url = None
    _header = None
    _lock = asyncio.Lock()
    _semaphore = asyncio.Semaphore(30)


    @classmethod
    async def connect(cls):
        cls._header = {
            'Authorization': f"Bearer {os.getenv('SLACK_TOKEN')}",
            'Content-Type': 'application/json'
        }
        cls._url = 'https://slack.com/api/chat.postMessage'
        cls._clients = httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=10, max_connections=500), timeout=30.0, headers=cls._header)
        logging.info("✅ connected Slack")


    @classmethod
    async def disconnect(cls):
        cls._base_url = None
        await cls._clients.aclose()
        logging.info("🔴 disconnected Slack")


    @classmethod
    async def _ensure_client(cls):
        """클라이언트가 없거나 닫혔으면 새로 생성"""
        if cls._clients is None or cls._clients.is_closed:
            async with cls._lock:
                if cls._clients is None or cls._clients.is_closed:
                    cls._clients = httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=10, max_connections=500), timeout=30.0, headers=cls._header)


    @classmethod
    async def _close_client(cls):
        cls._clients.aclose()
        cls._clients = None


    @classmethod
    @asynccontextmanager
    async def _get_client(cls):
        """Context manager로 안전한 클라이언트 사용"""
        await cls._ensure_client()
        try:
            yield cls._clients
        except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
            logging.warning(f"Connection 오류 발생, 클라이언트 재생성: {e}")
            await cls._close_client()
            await cls._ensure_client()
            yield cls._clients


    @classmethod
    async def send_message(cls, channel:str, message:str):
        try:
            message_object = {
                'channel': channel,
                'text': message
            }

            await cls._ensure_client()
            async with cls._semaphore:
                async with cls._get_client() as client:
                    response = await client.post(url=cls._url, json=message_object)
                    response.raise_for_status()
                    logging.info(f"[client.slack.SlackClient.send_message] Success to send message at {channel}")

        except Exception as e:
            logging.info(f"[client.slack.SlackClient.send_message] Fail to send message at {channel}. ERROR MESSAGE is {e}")
