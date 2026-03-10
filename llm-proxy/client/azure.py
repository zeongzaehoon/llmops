from openai import AsyncAzureOpenAI
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from openai.types.responses.response_in_progress_event import ResponseInProgressEvent
from openai.types.responses.response_output_item_done_event import ResponseOutputItemDoneEvent
from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from openai.types.responses.response_error import ResponseError

from client.common import *



class AzureClient:
    def __init__(self, data: ChatPayload | OcrChatPayload | ChatMCPPayload | EmbeddingsPayload, async_data: AsyncData = None):
        self.data = data
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.base_url = os.getenv('AZURE_OPENAI_BASE_URL')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        self.embedding_api_version = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
        self.async_data = async_data
        self._client = None  # 클라이언트 인스턴스 캐싱
        self._embedding_client = None


    def get_client(self):
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.base_url,
                api_version=self.api_version
            )
        return self._client


    def get_embedding_client(self):
        if self._embedding_client is None:
            self._embedding_client = AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.base_url,
                api_version=self.embedding_api_version
            )
        return self._embedding_client


    def get_system_prompt(self):
        system_message = self.data.system_message
        if self.data.system_message_placeholder:
            system_message = system_message.format_map(self.data.system_message_placeholder)
        return system_message


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
        messages = []
        history_messages = self.translate_conversation_history()
        if history_messages:
            messages.extend(history_messages)

        if not self.data.images:
            content = self.data.question
        else:
            content = [{"type": "input_text", "text": self.data.question}]
            for image, _type in zip(self.data.images, self.data.image_types):
                if _type == URL:
                    content.append({"type": "input_image", "image_url": image})

        last_message = {"role": "user", "content": content}
        messages.append(last_message)
        return messages


    async def embeddings(self, is_retry: bool = False):
        try:
            client = self.get_embedding_client()
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
            logging.error(f"session_key: {self.data.session_key} | [client.azure.AzureClient.embeddings] ERROR: {e}")
            raise FirstTryError() if not is_retry else SecondTryError()


    async def stream(self, is_retry:bool=None):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in OPENAI_MODEL_LIST else "gpt-4o"
            instruction = self.get_system_prompt()
            input = self.get_messages()
            reasoning = {"effort": "low"} if model in OPENAI_REASONING_MODEL_LIST else None

            logging.info(f"session_key: {self.data.session_key} | [client.azure.AzureClient.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to AZURE")

            async with asyncio.timeout(TIMEOUT) as timeout_cm:
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
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from AZURE: {elapsed}")
                        else:
                            response_dict["text"] = chunk.delta
                    if isinstance(chunk, ResponseInProgressEvent) and hasattr(chunk, "model"):
                        response_dict["model"] = chunk.model
                        response_dict["vendor"] = OPENAI
                    if isinstance(chunk, ResponseOutputItemDoneEvent):
                        response_dict["is_end"] = True
                    if isinstance(chunk, ResponseError):
                        response_dict["is_error"] = True

                    result = serialize_response(response_dict)
                    yield result
                    await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.azure.AzureClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.azure.AzureClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def chat(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in OPENAI_MODEL_LIST else "gpt-4o"
            instruction = self.get_system_prompt()
            input = self.get_messages()
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}
            else:
                reasoning = None

            logging.info(f"session_key: {self.data.session_key} | [client.azure.AzureClient.chat] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to AZURE")

            response = await client.responses.create(
                model = model,
                instructions=instruction,
                input=input,
                reasoning=reasoning,
                stream=False
            )

            response_dict = make_response(iteration=0)
            response_dict["text"] = response.output_text
            response_dict["vendor"] = OPENAI
            response_dict["model"] = response.model
            response_dict["is_end"] = True
            return response_dict

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.azure.AzureClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()


    async def stream_with_queue(self, is_retry: bool = False):
        try:
            client = self.get_client()
            model = self.data.model if not is_retry and self.data.model in OPENAI_MODEL_LIST else "gpt-4o"
            instruction = self.get_system_prompt()
            input = self.get_messages()
            reasoning = None
            if model in OPENAI_REASONING_MODEL_LIST:
                reasoning = {"effort": "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"}

            logging.info(f"session_key: {self.data.session_key} | [client.azure.AzureClient.stream_with_queue] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQEUST to AZURE")

            response = await client.responses.create(
                model = model,
                instructions=instruction,
                input=input,
                stream=True,
                reasoning=reasoning
            )

            is_first_res = True
            async for chunk in response:
                response_dict = make_response(iteration=0)
                if isinstance(chunk, ResponseTextDeltaEvent) and hasattr(chunk, "delta"):
                    if is_first_res:
                        if not self.async_data.event.is_set():
                            self.async_data.event.set()
                        response_dict["text"] = chunk.delta
                        is_first_res = False
                        if self.data.time:
                            time_first_req = time()
                            elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                            logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from AZURE: {elapsed}")
                    else:
                        response_dict["text"] = chunk.delta
                if isinstance(chunk, ResponseInProgressEvent) and hasattr(chunk, "model"):
                    response_dict["model"] = chunk.model
                    response_dict["vendor"] = AZURE
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
            logging.error(f"session_key: {self.data.session_key} | [client.azure.AzureClient.stream_with_queue] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                result = make_error_response()
                await self.async_data.queue.put(result)
                await self.async_data.queue.put(None)
