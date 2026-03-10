import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client



@dataclass
class FastMCPClient:
    mcp_url: str = os.getenv("MCP_SERVER_URL")
    mcp_token: str = None
    session: Optional[ClientSession] = None
    _read_stream = None
    _write_stream = None
    _client_context = None


    async def connect(self):
        try:
            headers = {}
            if self.mcp_token:
                headers["Authorization"] = f"Bearer {self.mcp_token}"

            self._client_context = streamablehttp_client(
                self.mcp_url,
                headers,
                timeout=120,
                terminate_on_close=False
            )

            self._read_stream, self._write_stream, _ = await self._client_context.__aenter__()
            self.session = ClientSession(self._read_stream, self._write_stream)
            await self.session.__aenter__()
            await self.session.initialize()

            logging.info(f"[FastMCPClient] Connected to MCP server: {self.mcp_url}")

        except Exception as e:
            logging.error(f"[FastMCPClient.connect] ERROR: {e}")
            raise


    async def disconnect(self):
        """MCP 서버 연결 종료"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._client_context:
                await self._client_context.__aexit__(None, None, None)
            logging.info(f"[FastMCPClient] Disconnected from MCP server")
        except Exception as e:
            logging.error(f"[FastMCPClient.disconnect] ERROR: {e}")


    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        # create_mcp_client에서 이미 connect()를 호출했으므로
        # 연결되지 않은 경우에만 연결
        if not self.session:
            await self.connect()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.disconnect()
        return False


    async def get_session(self):
        try:
            if not self.session:
                await self.connect()
            return self.session
        except Exception as e:
            logging.error(f"[FastMCPClient.get_session] ERROR: {e}")


    async def ping(self):
        """서버 상태 확인 (가벼운 health check)"""
        try:
            if not self.session:
                await self.connect()

            await self.session.send_ping()
            return True

        except (Exception, asyncio.CancelledError) as e:
            logging.error(f"[FastMCPClient.ping] ERROR: {e}")
            return False

        finally:
            try:
                await self.disconnect()
            except (Exception, asyncio.CancelledError):
                pass


    async def list_tools(self):
        try:
            if not self.session:
                await self.connect()

            result = await asyncio.wait_for(self.session.list_tools(), timeout=10)
            logging.info(f"[FastMCPClient.list_tools] Found {len(result.tools)} tools")

            # Bedrock format으로 변환
            tools = []
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                })

            return tools

        except (Exception, asyncio.CancelledError) as e:
            logging.error(f"[FastMCPClient.list_tools] ERROR: {e}")
            return False

        finally:
            try:
                await self.disconnect()
            except (Exception, asyncio.CancelledError):
                pass


    async def call_tool(self, tool_name: str, arguments: dict):
        """도구 실행"""
        try:
            if not self.session:
                await self.connect()

            logging.info(f"[FastMCPClient.call_tool] Calling tool: {tool_name} with args: {arguments}")
            result = await self.session.call_tool(tool_name, arguments)
            return result

        except Exception as e:
            logging.error(f"[FastMCPClient.call_tool] ERROR: {e}")
            raise

        finally:
            await self.disconnect()
