import openai
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_in_progress_event import ResponseInProgressEvent
from openai.types.responses.response_output_item_done_event import ResponseOutputItemDoneEvent
from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from openai.types.responses.response_error import ResponseError

from client.common import *



class OpenAIClient:
    def __init__(
            self,
            data: ChatPayload | OcrChatPayload | ChatMCPPayload | EmbeddingsPayload,
            async_data: AsyncData = None
    ):
        self.data = data
        self.async_data = async_data
        self._api_key = self.get_api_key()


    def get_api_key(self):
        api_key = os.getenv("OPENAI_API_KEY")
        return api_key


    def get_client(self):
        return openai.AsyncOpenAI(api_key=self._api_key)


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


    def get_messages(self):
        """
        messages = [
            {"role": "developer", "content": await self.get_system_prompt()},
            {"role": "user", "content": self.data.conversation_history if role == "human"},
            {"role": "assistant", "content": self.data.conversation_history if role == "ai"},
        ]
        """
        messages = []
        history_messages = self.translate_conversation_history()
        if history_messages:
            messages.extend(history_messages)

        if not self.data.images:
            content = self.data.question
        else:
            content = [{"type": "input_text", "text": self.data.question}]
            # for image, _type, extension in zip(self.data.images, self.data.image_types, self.data.image_filename_extensions):
            for image, _type in zip(self.data.images, self.data.image_types):
                if _type == URL:
                    # image_url = image if _type == URL else f"data:image/{extension};base64,{image}"
                    content.append({"type": "input_image", "image_url": image})
                else:
                    pass

        last_message = {"role": "user", "content": content}
        messages.append(last_message)
        return messages


    def get_mcp_tools(self):
        return [
            {
                "type": "mcp",
                "server_label": "knitlog_agent_server",
                "server_url": os.getenv("MCP_SERVER_URL"),
                "allowed_tools": ["get_current_time", "query_prescription_data"],
                "require_approval": "never",
                "headers": {"Authorization": f"Bearer {self.data.mcp_token}"}
            }
        ]


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


    async def embeddings(self, is_retry: bool = False):
        try:
            client = self.get_client()
            response = await client.embeddings.create(
                model=self.data.model,
                input=self.data.text
            )
            if isinstance(self.data.text, list):
                vector = list()
                for v in response.data:
                    np_vector = np.array(v.embedding, dtype=np.float32)
                    base64_vector = base64.b64encode(np_vector.tobytes()).decode('utf-8')
                    vector.append(base64_vector)
            else:
                np_vector = np.array(response.data[0].embedding, dtype=np.float32)
                base64_vector = base64.b64encode(np_vector.tobytes()).decode('utf-8')
                vector = base64_vector
            return vector
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.openai.OpenAIClient.embeddings] ERROR: {e}")
            raise FirstTryError() if not is_retry else SecondTryError()


    async def stream(self, is_retry:bool=None):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in OPENAI_MODEL_LIST else OPENAI_MODEL_LIST[0]
            instruction = self.get_system_prompt()
            input = self.get_messages()
            reasoning = None
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}

            logging.info(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} |  REQUEST to OPENAI")

            async with asyncio.timeout(30 if self.data.model == "gpt-5.2-pro" else TIMEOUT) as timeout_cm:
                response = await client.responses.create(
                    model = model,
                    instructions=instruction,
                    input=input,
                    reasoning=reasoning,
                    stream=True
                )

                is_first_res = True
                async for chunk in response:
                    response_dict = make_response(iteration=0) # {"iteration": 0, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                    if isinstance(chunk, ResponseTextDeltaEvent) and hasattr(chunk, "delta"):
                        if is_first_res:
                            response_dict["text"] = chunk.delta
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from OPENAI: {elapsed}")
                        else:
                            response_dict["text"] = chunk.delta
                    if isinstance(chunk, ResponseCreatedEvent) and hasattr(chunk, "response") and hasattr(chunk.response, "model"):
                        response_dict["model"] = chunk.response.model
                        response_dict["vendor"] = OPENAI
                    if isinstance(chunk, ResponseOutputItemDoneEvent):
                        response_dict["is_end"] = True
                    if isinstance(chunk, ResponseError):
                        response_dict["is_error"] = True

                    if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                        result = serialize_response(response_dict)
                        yield result
                        await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def stream_with_mcp(self, is_retry:bool = False):
        try:
            client = self.get_client()
            model = self.data.model or "gpt-5.2"
            # model = self.data.model
            instruction = self.get_system_prompt()
            input = self.data.question
            tools = self.get_mcp_tools()
            reasoning = None
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}

            logging.info(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream_with_mcp] service: {self.data.service} | model: {model} | is_retry: {is_retry} | activate llm_with_mcp. vendor is openAI")

            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                response = await client.responses.create(
                    model=model,
                    instructions=instruction,
                    input=input,
                    stream=True,
                    reasoning=reasoning,
                    tools=tools
                )

                is_first_res = True
                async for chunk in response:
                    response_dict = make_response(iteration=0) # {"iteration": 0, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                    if isinstance(chunk, ResponseTextDeltaEvent) and hasattr(chunk, "delta"):
                        if is_first_res:
                            response_dict["text"] = chunk.delta
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from OPENAI: {elapsed}")
                        else:
                            response_dict["text"] = chunk.delta

                    if isinstance(chunk, ResponseCreatedEvent) and hasattr(chunk, "response") and hasattr(chunk.response, "model"):
                        response_dict["model"] = chunk.response.model
                        response_dict["vendor"] = OPENAI
                    if isinstance(chunk, ResponseOutputItemAddedEvent):
                        logging.info(f"session_key: {self.data.session_key} | [ResponseOutputItemAddedEvent] {chunk}")
                    if isinstance(chunk, ResponseOutputItemDoneEvent):
                        response_dict["is_end"] = True
                    if isinstance(chunk, ResponseError):
                        response_dict["is_error"] = True

                    if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                        result = serialize_response(response_dict)
                        yield result
                        await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream_with_mcp] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream_with_mcp] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def chat(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model
            instruction = self.get_system_prompt()
            input = self.get_messages()
            reasoning = None
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}

            logging.info(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.chat] service: {self.data.service} |  REQEUST to OPENAI")

            response = await client.responses.create(
                model = model,
                instructions=instruction,
                input=input,
                reasoning=reasoning,
                stream=False,
            )

            response_dict = make_response(iteration=0)
            response_dict["text"] = response.output_text
            response_dict["vendor"] = OPENAI
            response_dict["model"] = response.model
            response_dict["is_end"] = True
            return response_dict

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()



    async def stream_with_queue(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model
            instruction = self.get_system_prompt()
            input = self.get_messages()
            reasoning = None
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}

            logging.info(f"session_key: {self.data.session_key} | [client.open_ai.OpenAIClient.stream_with_queue] REQEUST to openAI")

            response = await client.responses.create(
                model = model,
                instructions=instruction,
                input=input,
                stream=True,
                reasoning=reasoning
            )

            is_first_res = True
            async for chunk in response:
                response_dict = make_response(iteration=0) # {"iteration": 0, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                if isinstance(chunk, ResponseTextDeltaEvent) and hasattr(chunk, "delta"):
                    if is_first_res:
                        if not self.async_data.event.is_set():
                            self.async_data.event.set()
                        response_dict["text"] = chunk.delta
                        is_first_res = False
                        if self.data.time:
                            time_first_req = time()
                            elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                            logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from OPENAI: {elapsed}")
                    else:
                        response_dict["text"] = chunk.delta
                if isinstance(chunk, ResponseInProgressEvent) and hasattr(chunk, "model"):
                    response_dict["model"] = chunk.model
                    response_dict["vendor"] = OPENAI
                if isinstance(chunk, ResponseOutputItemDoneEvent):
                    response_dict["is_end"] = True
                if isinstance(chunk, ResponseError):
                    response_dict["is_error"] = True

                if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                    result = serialize_response(response_dict)
                    await self.async_data.queue.put(result)
                    await asyncio.sleep(0)

            await self.async_data.queue.put(None)  # 스트림 종료 신호

        except Exception as e:
            # 에러 로깅
            logging.error(f"session_key: {self.data.session_key} | [client.openai.OpenAIClient.stream_with_queue] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                result = make_error_response()
                await self.async_data.queue.put(result)
                await self.async_data.queue.put(None)
