import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@dataclass
class FastMCPClient:
    mcp_url: str = os.getenv("MCP_SERVER_URI")
    mcp_token: str = None
    session_key: str = None
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
                timeout=30,
                terminate_on_close=False
            )

            self._read_stream, self._write_stream, _ = await self._client_context.__aenter__()
            self.session = ClientSession(self._read_stream, self._write_stream)
            await self.session.__aenter__()
            await self.session.initialize()

            logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} |  [FastMCPClient] Connected to MCP server: {self.mcp_url}")

        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.connect] ERROR: {e}")
            raise


    async def disconnect(self):
        """MCP 서버 연결 종료"""
        try:
            if self.session:
                try:
                    await self.session.__aexit__(None, None, None)
                except:
                    pass  # session 종료 중 에러 무시
                finally:
                    self.session = None

            if self._client_context:
                try:
                    await self._client_context.__aexit__(None, None, None)
                except (RuntimeError, BaseException) as e:
                    # anyio task group의 cancel scope 문제는 무시 (기능상 문제 없음)
                    if "cancel scope" in str(e) or "task" in str(e).lower():
                        pass  # 무시
                    else:
                        logging.warning(f"session_key: {self.session_key} | [FastMCPClient.disconnect] Context cleanup error: {e}")
                finally:
                    self._client_context = None
                    self._read_stream = None
                    self._write_stream = None

            logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient] Disconnected from MCP server")
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.disconnect] ERROR: {e}")


    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        # create_mcp_client에서 이미 connect()를 호출했으므로
        # 연결되지 않은 경우에만 연결
        try:
            if not self.session:
                await self.connect()
            return self
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.connect] ERROR: {e}")
            raise e


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        try:
            await self.disconnect()
            return False
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.disconnect] ERROR: {e}")
            raise e


    async def get_session(self):
        try:
            if not self.session:
                await self.connect()
            return self.session
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.get_session] ERROR: {e}")
            raise e


    async def list_tools(self, timeout: int = None):
        try:
            if not timeout:
                timeout = 30

            async with asyncio.timeout(timeout):
                if not self.session:
                    await self.connect()
                logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.list_tools] REQUEST Found tools to mcp server")
                result = await self.session.list_tools()
                logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.list_tools] RECEIVED Found {len(result.tools)} tools from mcp server")

                tools = []
                for tool in result.tools:
                    tools.append({
                        "name": tool.name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                    })

                return tools

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.list_tools] TIMEOUT ERROR: {timeout}")
            raise Exception(f"MCP list_tools timed out after {timeout}s")
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.list_tools] ERROR: {e}")
            raise e


    async def call_tool(self, tool_name: str, arguments: dict, timeout: int = None):
        """도구 실행"""
        try:
            if not timeout:
                timeout = 180

            async with asyncio.timeout(timeout):
                if not self.session:
                    await self.connect()
                logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.call_tool] REQUEST Calling tool: {tool_name} with args: {arguments} to mcp server")
                result = await self.session.call_tool(tool_name, arguments)
                logging.info(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.call_tool] RECEIVED Calling tool: {tool_name} with args: {arguments} from mcp server")
                return result

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.call_tool] TIMEOUT ERROR: {timeout}")
            raise Exception(f"MCP call_tool '{tool_name}' timed out after {timeout}s")
        except Exception as e:
            logging.error(f"session_key: {self.session_key} | mcp_url: {self.mcp_url} | [FastMCPClient.call_tool] ERROR: {e}")
            raise e


async def create_mcp_client(mcp_url: str, mcp_token: str = None, session_key: str = None):
    try:
        client = FastMCPClient(mcp_url, mcp_token, session_key)
        await client.connect()
        return client
    except Exception as e:
        logging.error(f"session_key: {session_key} | mcp_url: {mcp_url} | [FastMCPClient] ERROR: {e}")
        raise e
