from module.mcp.run import *
from module.mcp.dto import *

from utils.error import *



class RunMCP:
    """
    # RunMCP do\n
    ---\n
    1. mainDB에서 요청에 맞는 시스템 프롬프트 쿼리\n
    2. memoryDB에 저장된 대화이력 조회\n
    3. FastTextDetector(DL) 활용해 사용자 질문 언어 판별 | 일본어 답변을 제대로 못해 조치\n
    5. [1, 2, 3] I/O를 비동기로 동시에 진행\n
    6. llm-proxy api 요청 | client.groxy.LLMProxyClient.stream_with_mcp 코드 참고\n
    7. 답변 객체 or 텍스트를 제네레이터로 RunLLM 호출한 객체에 전달(streaming message)\n
    8. 답변 완료 후, module.LLM.run.callback에서 크레딧, 답변 기록 등 후처리 진행\n
    """


    def __init__(self, args:dict, thread:bool=None, stream:bool=None):
        self.args:dict = args
        self.thread = thread if thread is not None else True
        self.stream = stream if stream is not None else True

    async def activate(self):
        try:
            tasks = []
            self._get_mcpArgs()
            tasks.append(self._get_model())
            tasks.append(self._get_conversation_history())
            tasks.append(self._get_prompt())
            tasks.append(self._get_mcp_agent_info())
            await asyncio.gather(*tasks)
            async for chunk in self._run():
                yield chunk

        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 DBError: {e.message}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: DBError"
                    await message_client.send_message(channel='casual', message=message)

        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 MemoryDBError: {e.message}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: MemoryDBError"
                    await message_client.send_message(channel='casual', message=message)

        except VectorDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 VectorDBError: {e.message}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: VectorDBError"
                    await message_client.send_message(channel='casual', message=message)

        except AWSError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 AWSError: {e.message}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: AWSError"
                    await message_client.send_message(channel='casual', message=message)

        except LLMStreamingError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 LLMStreamingError: {e.message}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: LLMStreamingError"
                    await message_client.send_message(channel='casual', message=message)

        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate] 🔴 Exception: {e}")
            response = make_error_message(agent=self.args.get("agent"), lang=self.args.get('lang'))
            yield orjson.dumps(response) if isinstance(response, dict) else response
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: Exception"
                    await message_client.send_message(channel='casual', message=message)


    async def _run(self):
        try:
            async for chunk in run_mcp(self.mcpArgs):
                yield chunk
        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 MemoryDBError: {e.message}")
            raise MemoryDBError(e.message)
        except VectorDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 VectorDBError: {e.message}")
            raise VectorDBError(e.message)
        except AWSError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 AWSError: {e.message}")
            raise AWSError(e.message)
        except LLMStreamingError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 LLMStreamingError: {e.message}")
            raise LLMStreamingError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._run] 🔴 Exception: {e}")
            raise e


    def _get_mcpArgs(self):
        try:
            if not self.args or not isinstance(self.args, dict):
                raise ValueError("params is required and must be dict")
            self.mcpArgs:MCPArgs = make_mcpArgs(self.args)
        except ValueError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_mcpArgs] 🔴 ValueError: {e}")
            raise e
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_mcpArgs] 🔴 Exception: {e}")
            raise e


    async def _get_model(self):
        try:
            if not self.mcpArgs.model:
                logging.info(f"session_key: {self.args.get('session_key')} | model is not selected. Get VENDOR & MODEL")
                self.mcpArgs.vendor, self.mcpArgs.model = await get_vendor_and_model(mcpArgs=self.mcpArgs)

            logging.info(f"session_key: {self.args.get('session_key')} | [module.dashboard.activate._get_model] vendor: {self.mcpArgs.vendor}, model: {self.mcpArgs.model}")
            self.mcpArgs.chat_info["model"] = self.mcpArgs.model
            self.mcpArgs.chat_info["vendor"] = self.mcpArgs.vendor

        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_model] 🔴 DBError: {e.message}]")
            raise DBError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_model] 🔴 Exception: {e}")
            raise e


    async def _get_conversation_history(self):
        try:
            conversation_history = await get_conversation_history(self.mcpArgs) # memory_db_client, session_key
            self.mcpArgs.conversation_history = mcp_conv_hist_format(conversation_history)
        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_conversation_history] 🔴 MemoryDBError: {e}")
            raise MemoryDBError(e)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_conversation_history] 🔴 Exception: {e}")
            raise e


    async def _get_prompt(self):
        try:
            self.mcpArgs.system_message, self.mcpArgs.chat_info["pid"] = await get_system_prompt(self.mcpArgs) # main_db_client, company_key
        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_prompt] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_prompt] 🔴 Exception: {e}")
            raise e


    async def _get_mcp_agent_info(self):
        try:
            self.mcpArgs.mcp_info = await get_mcp_toolset(self.mcpArgs)
        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_mcp_agent_info] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.mcp.activate._get_mcp_agent_info] 🔴 Exception: {e}")
            raise e
