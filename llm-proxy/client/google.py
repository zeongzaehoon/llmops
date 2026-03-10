import httpx

from google import genai
from google.genai.types import AutomaticFunctionCallingConfig, ThinkingConfig, GenerateContentConfig, ThinkingLevel

from models.file import *
from client.common import *



class GoogleClientConnector:
    def __init__(
        self,
        data: ChatPayload | OcrChatPayload = None,
        file_data: CreateStorePayload | GetStoresPayload | ImportFilePayload | GetFilesPayload | DeleteStorePayload | DeleteDocumentPayload = None,
        async_data: AsyncData = None
    ):

        self.data = data
        self.file_data = file_data
        self.async_data = async_data
        self._api_key = self.get_api_key()


    def get_api_key(self):
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            return api_key
        except Exception as e:
            logging.error(f"[client.google.GoogleClientConnector.get_api_key] Fail to return Client: {e}")  # session_key not available here
            raise Exception(e)


    def get_client(self):
        try:
            return genai.Client(api_key=self._api_key)
        except Exception as e:
            logging.error(f"[client.google.GoogleClientConnector.get_client] Fail to return Client: {e}")
            raise Exception(e)



class GoogleClient(GoogleClientConnector):
    def get_system_prompt(self):
        system_message = self.data.system_message
        if self.data.system_message_placeholder:
            system_message = system_message.format_map(self.data.system_message_placeholder)
        return str(system_message)


    def translate_conversation_history(self):
        if not self.data.conversation_history:
            return None

        result = []
        pending_user = None

        for data in self.data.conversation_history:
            role = "assistant" if data.get("role") in ["ai", "assistant"] else "user"
            content = data.get("message") or data.get("content")

            if role == "user":
                pending_user = {"role": "user", "content": content}
            elif role == "assistant" and pending_user:
                # user-assistant 쌍 완성
                result.extend([pending_user, {"role": "assistant", "content": content}])
                pending_user = None

        return result if result else None


    async def get_messages_for_gemini(self):
        messages = []
        history_messages = self.translate_conversation_history()

        if history_messages:
            for msg in history_messages:
                role = 'model' if msg['role'] == 'assistant' else 'user'
                messages.append({
                    "role": role,
                    "parts": [{"text": msg['content']}]
                })

        # 마지막 사용자 메시지
        parts = list()
        if self.data.images:
            async with httpx.AsyncClient() as client:
                # for image, _type, extension in zip(self.data.images, self.data.image_types, self.data.image_filename_extensions):
                for image, _type in zip(self.data.images, self.data.image_types):
                    if _type == URL:
                        # TODO@jaehoon: 지원 외 content-type으로 response가 내려가는 url이면 에러가 남. 일단 어떤 이미지든 받을 수 있게 base64로 바꿔 진행. 불필요한 I/O 비용 추가니, 시간날 때마다 개선방안 체크해볼 것
                        response = await client.get(image)
                        image_bytes = response.content

                        # 실제 이미지 데이터에서 타입 감지
                        detected_type = detect_image_format(image_bytes)
                        if detected_type:
                            mime_type = f"image/{detected_type}"
                        else:
                            # 감지 실패시 extension fallback
                            mime_type = f"image/jpeg"

                        image_part = genai.types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type
                        )
                        parts.append(image_part)
                    elif _type == BASE64:
                        pass
                        # image_bytes = base64.b64decode(image)
                        # image_part = genai.types.Part.from_bytes(
                        #     data=image_bytes,
                        #     mime_type=f"image/{extension}"
                        # )
                        # parts.append(image_part)

        parts.append({"text": self.data.question})

        messages.append({
            "role": "user",
            "parts": parts
        })

        return messages


    def translate_tools_for_function_call(self):
        """
        tools = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current temperature for provided coordinates in celsius.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }]
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "parameters": tool.get("parameters"),
                    "strict": tool.get("strict")
                }
            }
            for tool in self.data.tools
        ]


    async def stream(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in GOOGLE_MODEL_LIST else "gemini-2.5-flash"
            contents = await self.get_messages_for_gemini()
            system_instruction = self.get_system_prompt()
            tools= [
                genai.types.Tool(
                    file_search=genai.types.FileSearch(
                        file_search_store_names=[self.data.store_name],
                        top_k=5,
                        metadata_filter=self.data.metadata_filter # metadata_filter="author=Robert Graves",
                    )
                )
            ] if self.data.store_name else None
            thinking_config = ThinkingConfig(include_thoughts=False, thinking_budget=0) if self.data.service in KNITLOG_SERVICES else None

            logging.info(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to Google")

            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                response = await client.aio.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0,
                        tools=tools,
                        thinking_config=thinking_config
                    ),
                )

                is_first_res = True
                iteration = 0
                texts = None
                async for chunk in response:
                    response_dict = make_response(iteration) # {"iteration": 0, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                    if hasattr(chunk, "model_version") and chunk.model_version:
                        response_dict["model"] = chunk.model_version
                        response_dict["vendor"] = GOOGLE
                    if hasattr(chunk, 'candidates') and chunk.candidates:
                        if is_first_res:
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from GOOGLE: {elapsed}")

                        if chunk.candidates[0] and hasattr(chunk.candidates[0], "content"):
                            candidate = chunk.candidates[0]
                            content = candidate.content
                            if content and hasattr(content, "parts") and content.parts:
                                for part in content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        # response_dict["text"] = part.text
                                        texts = part.text

                            if hasattr(candidate, "finish_reason") and candidate.finish_reason:
                                response_dict["is_end"] = True
                                iteration += 1

                    if any([texts, response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                        if texts: # 텍스트가 너무 큼. chunking을 잘개 쪼개서 진행
                            for text in texts:
                                response_dict["text"] = text
                                result = serialize_response(response_dict)
                                yield result
                                await asyncio.sleep(0.01)
                            texts = None
                            await asyncio.sleep(0)
                        else:
                            result = serialize_response(response_dict)
                            yield result
                            await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def stream_with_mcp(self, is_retry: bool = False):
        try:
            client = self.get_client()
            mcp_client = await create_mcp_client(os.getenv("MCP_SERVER_URL"), getattr(self.data, 'mcp_token', None), self.data.session_key)
            model = self.data.model if not is_retry and self.data.model in GOOGLE_MODEL_LIST else "gemini-2.5-flash"
            contents = await self.get_messages_for_gemini()
            system_instruction = self.get_system_prompt()
            automatic_function_calling=AutomaticFunctionCallingConfig(maximum_remote_calls=10)
            # automatic_function_calling = {"maximum_remote_calls": 10}

            logging.info(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream_with_mcp] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to GOOGLE MCP")
            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                async with mcp_client:
                    response = await client.aio.models.generate_content_stream(
                        model="gemini-2.5-flash",
                        contents=contents,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0,
                            automatic_function_calling=automatic_function_calling,
                            tools=[mcp_client.session],
                        ),
                    )

                    is_first_res = True
                    iteration = 0
                    async for chunk in response:
                        response_dict = make_response(iteration) # {"iteration": 0, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                        if hasattr(chunk, "model_version") and chunk.model_version:
                            response_dict["model"] = chunk.model_version
                            response_dict["vendor"] = GOOGLE
                        if hasattr(chunk, 'candidates') and chunk.candidates:
                            if is_first_res:
                                is_first_res = False
                                timeout_cm.reschedule(None)
                                if self.data.time:
                                    time_first_req = time()
                                    elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                    logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from GOOGLE MCP: {elapsed}")

                            candidate = chunk.candidates[0]
                            content = candidate.content
                            if content and content.parts:
                                for part in content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        response_dict["text"] = part.text
                                    if hasattr(part, "function_call"):
                                        func_call = part.function_call
                                        response_dict["tool_name"] = func_call.name if hasattr(func_call, "name") else None
                                        response_dict["tool_text"] = str(func_call.args) if hasattr(func_call, "args") else None
                                        response_dict["text"] = "\n\n\n" if func_call else response_dict["text"]

                            if hasattr(candidate, "finish_reason") and candidate.finish_reason:
                                response_dict["is_end"] = True
                                iteration += 1

                        if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                            result = serialize_response(response_dict)
                            yield result
                            await asyncio.sleep(0)


        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream_with_mcp] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream_with_mcp] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def chat(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in GOOGLE_MODEL_LIST else "gemini-2.5-flash"
            contents = await self.get_messages_for_gemini ()
            system_instruction = self.get_system_prompt()

            logging.info(f"session_key: {self.data.session_key} | [client.google.GoogleClient.stream_with_mcp] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to GOOGLE MCP")

            response = await client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0,
                ),
            )
            response_dict = make_response(0)
            response_dict["text"] = response.candidates[0].content.parts[0].text
            response_dict["vendor"] = GOOGLE
            response_dict["model"] = response.model_version
            response_dict["is_end"] = True
            return response_dict

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.google.GoogleClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()



class GoogleFileSearchClient(GoogleClientConnector):
    async def create_file_search_store(self, display_name=None):
        try:
            client = self.get_client()

            config = {}
            if display_name:
                config["display_name"] = display_name

            response = await client.aio.file_search_stores.create(config=config)
            logging.info(f"[client.google.GoogleFileSearchClient.create_file_search_store] store_name: {response.name} | display_name: {display_name}")
            return response.name

        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.create_file_search_store] ERROR: {e}")
            raise Exception(e)


    async def get_list_file_search_store(self):
        try:
            client = self.get_client()
            result = await client.aio.file_search_stores.list()
            stores = []
            async for store in result:
                store_dict = {
                    'name': store.name if hasattr(store, 'name') else None,
                    'display_name': store.display_name if hasattr(store, 'display_name') else None,
                    'create_time': str(store.create_time) if hasattr(store, 'create_time') else None,
                    'update_time': str(store.update_time) if hasattr(store, 'update_time') else None,
                }
                stores.append(store_dict)
            return stores
        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.get_list_file_search_store] ERROR: {e}")
            raise Exception(e)


    async def upload_file_in_file_search_store(self, store_name, file_path, file_name):
        try:
            client = self.get_client()
            config = {
                'chunking_config': {
                    'white_space_config': {
                        'max_tokens_per_chunk': FILESEARCH_CHUNKING_TOKEN,
                        'max_overlap_tokens': FILESEARCH_CHUNKING_OVERLAPS_TOKEN
                    }
                },
                'display_name': file_name
            }

            response = await client.aio.file_search_stores.upload_to_file_search_store(
                file_search_store_name=store_name,
                file=file_path,
                config=config
            )

            cnt = 0
            max_retries = 20
            while not response.done or cnt >= max_retries:
                await asyncio.sleep(5)
                response = await client.aio.operations.get(response)
                cnt += 1

            return response.name if hasattr(response, 'name') else ""

        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.upload_file_in_file_search_store] ERROR: {e}")
            raise Exception(e)


    async def get_all_file_in_file_search_store(self, store_name, page_size=None):
        try:
            page_size = page_size or 20

            client = self.get_client()

            config = None
            if page_size:
                config = {'page_size': page_size}

            documents = await client.aio.file_search_stores.documents.list(parent=store_name, config=config)
            files = list()
            async for doc in documents:
                doc_dict = {
                    'name': doc.name if hasattr(doc, 'name') else None,
                    'display_name': doc.display_name if hasattr(doc, 'display_name') else None,
                    'create_time': str(doc.create_time) if hasattr(doc, 'create_time') else None,
                    'update_time': str(doc.update_time) if hasattr(doc, 'update_time') else None,
                }
                files.append(doc_dict)

            return files

        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.get_all_file_in_file_search_store] ERROR: {e}")
            raise Exception(e)


    async def delete_file_search_store(self, store_name):
        try:
            client = self.get_client()
            config = {"force": True}
            await client.aio.file_search_stores.delete(name=store_name, config=config)

        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.delete_file_search_store] ERROR: {e}")
            raise Exception(e)


    async def delete_file_in_file_search_store(self, document_name):
        try:
            client = self.get_client()
            config = {"force": True}
            await client.aio.file_search_stores.documents.delete(name=document_name, config=config)

        except Exception as e:
            logging.error(f"[client.google.GoogleFileSearchClient.delete_file_in_file_search_store] ERROR: {e}")
            raise Exception(e)
