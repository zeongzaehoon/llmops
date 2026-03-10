from uuid import uuid4

from module.llm.helper import *
from module.llm.run import *
from module.llm.dto import *

from utils.constants import *
from utils.error import *



class RunLLM:
    """
    # RunLLM do\n
    ---\n
    1. mainDB에서 요청에 맞는 시스템 프롬프트 가져오기\n\n
    2. 참고 데이터 가져오기\n
    2-1. 일반 챗봇엔 vectorDB에서 사용자 질문 의미와 가장 가까운 데이터 검색 -> mysql, s3 등에서 원천 데이터 가져오기\n
    2-2. docent, dashboardChat처럼 보고서 기반 챗봇엔 메모리 DB에 담긴 보고서 내용 및 원천 데이터 가져오기\n
    2-3. aireport엔 RAG가 필요없으므로 생략\n
    3. memoryDB에 저장된 대화이력 가져오기\n\n
    4. FastTextDetector(DL) 활용한 사용자 질문 언어 판별 | 다국어 처리 중 일본어 답변 문제로 추가\n
    5. [1, 2, 3, 4] I/O를 비동기로 동시에 진행\n
    6. llm-proxy api 요청하기 | client.groxy.LLMProxyClient.stream 코드 참고\n
    7. 답변 객체 or 텍스트를 제네레이터로 RunLLM 호출한 객체에 전달하기(streaming message)\n
    8. 답변 완료 후, 크레딧, 답변 기록 등 후처리 | module.LLM.run.callback
    """

    def __init__(self, args:dict, thread:bool=None, stream:bool=None):
        self.args = args
        self.thread = thread or True
        self.stream = stream or True
        self.args["streaming"] = self.stream
        self.llmArgs: LLMArgs


    async def activate(self):
        try:
            tasks = []
            await self._get_llmArgs()
            await self._get_query()
            if self.llmArgs.agent in DOCENT_LIST:
                tasks.append(self._get_report_and_data_from_main_db())
            elif self.llmArgs.agent not in [ABTEST, SCHEMATAG]:
                tasks.append(self._get_retrieval_data())
            tasks.append(self.get_conversation_history())
            tasks.append(self._get_prompt())
            tasks.append(self._get_model())
            await asyncio.gather(*tasks)
            async for chunk in self._run():
                yield chunk

        # raise ERROR X -> generating MESSAGE on lazy | async streaming pipe 내부에서 터지면 api side에서 raise된 error를 catch 못함
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate.activate] 🔴 Exception: {e}")
            for chunk in make_error_message(self.args.get('lang')):
                yield chunk
            if self.args.get("server_stage") == PRODUCTION and self.args.get("agent") in ON_PRODUCTION_LIST:
                await record_err_to_main_db(self.args)
                if self.args.get("message_client"):
                    message_client:SlackClient = self.args["message_client"]
                    message = f"🔴 session_key: {self.args.get('session_key')}, agent: {self.args.get('agent')} | [solomon-api] API module Error: Exception"
                    await message_client.send_message(channel='casual', message=message)


    async def _run(self):
        try:
            if self.llmArgs.agent in DOCENT_LIST:
                async for chunk in run_docent_llm(self.llmArgs):
                    yield chunk
            elif self.llmArgs.agent == VOC:
                async for chunk in run_voc_llm(self.llmArgs):
                    yield chunk
            elif self.llmArgs.agent == ABTEST:
                async for chunk in run_abtest_llm(self.llmArgs):
                    yield chunk
            elif self.llmArgs.agent == SCHEMATAG:
                async for chunk in run_schematag_llm(self.llmArgs):
                    yield chunk
            elif self.llmArgs.agent in DASHBOARD_LIST:
                async for chunk in run_dashboard_llm(self.llmArgs):
                    yield chunk
            else:
                async for chunk in run_llm(self.llmArgs):
                    yield chunk

        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 MemoryDBError: {e.message}")
            raise MemoryDBError(e.message)
        except VectorDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 VectorDBError: {e.message}")
            raise VectorDBError(e.message)
        except AWSError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 AWSError: {e.message}")
            raise AWSError(e.message)
        except LLMStreamingError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 LLMStreamingError: {e.message}")
            raise LLMStreamingError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._run] 🔴 Exception: {e}")
            raise e


    async def _get_llmArgs(self):
        """
        llm 모듈에 필요한 인자로 변경 - LLMArgs dataclass 사용
        """
        if not self.args or not isinstance(self.args, dict):
            raise ValueError("params is required and must be dict")
        self.llmArgs = await make_llmArgs(self.args)


    async def _get_query(self):
        try:
            self.query_prompt, qid = await get_query_prompt(self.llmArgs)
            self.llmArgs.insert_mongo["qid"] = qid

        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_query] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_query] 🔴 Exception: {e}")
            raise e


    async def _get_report_and_data_from_main_db(self):
        try:
            self.llmArgs.selected_report_data = await self.llmArgs.memory_db_client.get(key=f"rc:{self.args['session_key']}")
            self.llmArgs.retrieval_data = get_common_sense_data(self.llmArgs.init_date)

        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_report_and_data_from_main_db] 🔴 MemoryDBError: {e.message}")
            raise MemoryDBError(e)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_report_and_data_from_main_db] 🔴 Exception: {e}")
            raise e


    async def _get_retrieval_data(self):
        try:
            retrieval_result = await get_retrieval_data_for_rag(
                llm_proxy_client=self.llmArgs.llm_proxy_client,
                vector_db_client=self.llmArgs.vector_db_client,
                vector_query=self.query_prompt,
                k=4,
                init_date=self.llmArgs.init_date
            )
            self.llmArgs.retrieval_data = retrieval_result["retrieval_data"]
            self.llmArgs.insert_mongo["rid"] = retrieval_result["rid"]

        except VectorDBError as e:
            logging.info(f"session_key: {self.args.get('session_key')} | [llm.proxy._get_retrieval_data] 🔴 VectorDBError: {e}")
            raise VectorDBError(e)
        except Exception as e:
            logging.info(f"session_key: {self.args.get('session_key')} | [llm.proxy._get_retrieval_data] 🔴 Exception: {e}")
            raise e


    async def get_conversation_history(self):
        try:
            if self.llmArgs.redis_save:
                self.llmArgs.conversation_history = await get_conversation_history_for_llm(
                    self.llmArgs.memory_db_client,
                    self.args["session_key"]
                )
            else:
                self.llmArgs.convesation_history = []

        except MemoryDBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate.get_conversation_history] 🔴 MemoryDBError: {e.message}")
            raise MemoryDBError(e.message)
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate.get_conversation_history] 🔴 Exception: {e}")
            raise e


    async def _get_prompt(self):
        try:
            if not self.llmArgs:
                raise ValueError("llmArgs is required")

            prompt_category = CS if self.llmArgs.agent in UXGPT_LIST else self.llmArgs.agent

            # GET PROMPT FROM MONGO
            self.prompt, pid = await get_system_prompt(
                self.llmArgs.main_db_client,
                prompt_category,
                self.llmArgs.roleNameList or [],
                self.llmArgs.roleNameListForPlus or []
            )

            # ADD SYSTEM PROMPT
            if self.llmArgs.agent in UXGPT_LIST:
                self.prompt = self.prompt + "\n\n\n" + RAG_PROMPT
            if self.llmArgs.redis_save:
                self.prompt = self.prompt + '\n\n\n' + CONVERSATION_HISTORY
            if self.llmArgs.init_date and self.llmArgs.agent not in REPORT_LIST:
                self.prompt = self.prompt + '\n\n\n' + TIME_PROMPT

            # SET PROMPT DATA IN LLM ARGS
            self.llmArgs.insert_mongo["pid"] = pid
            self.llmArgs.insert_mongo["agent"] = self.llmArgs.agent
            if self.llmArgs.indepth:
                self.llmArgs.insert_mongo["tid"] = self.llmArgs.aireportId or str(uuid4())

            # SET
            self.llmArgs.system_message = self.prompt

        except DBError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_prompt] 🔴 DBError: {e.message}")
            raise DBError(e.message)
        except ValueError as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_prompt] 🔴 ValueError: {e}")
            raise ValueError
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_prompt] 🔴 Exception: {e}")
            raise e


    async def _get_model(self):
        try:
            if not self.llmArgs.model:
                logging.info("session_key: {self.args.get('session_key')} | model is not selected. Get VENDOR & MODEL")
                model_category = CS if self.llmArgs.agent in UXGPT_LIST else self.llmArgs.agent

                self.llmArgs.vendor, self.llmArgs.model = await get_vendor_and_model(
                    self.llmArgs.main_db_client,
                    model_category
                )

            self.llmArgs.insert_mongo["model"] = self.llmArgs.model
            self.llmArgs.insert_mongo["vendor"] = self.llmArgs.vendor
        except Exception as e:
            logging.error(f"session_key: {self.args.get('session_key')} | [module.llm.activate._get_model] 🔴 Exception: {e}")
            raise e



    # for client
    @classmethod
    async def get_retrieval_data_for_view(cls, llm_proxy_client, vector_db_client, question, service, k:int=4):
        return await get_retrieval_data_for_view(llm_proxy_client, vector_db_client, question, service, k=k)


    @classmethod
    async def get_retrieval_data_for_report_chat(cls, memory_db_client, session_key):
        tasks = [
            memory_db_client.get(key=f"rc:{session_key}"),
            memory_db_client.get(key=f"rc_id:{session_key}")
        ]
        result = await asyncio.gather(*tasks)
        return [
            {
                "content": result[0],
                "subject": result[1]
            }
        ]
