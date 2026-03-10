import httpx

# import openai
from xai_sdk import AsyncClient
from xai_sdk.chat import system, assistant, user, image, Chunk, Response

from client.common import *


@dataclass
class XClient:
    data: ChatPayload | OcrChatPayload | ChatMCPPayload
    async_data: AsyncData = None


    def get_api_key(self):
        api_key = os.getenv("XAI_API_KEY")
        return api_key


    def get_client(self):
        return AsyncClient(
            api_key=self.get_api_key(),
            timeout=3600
        )


    def get_system_prompt(self):
        system_message = self.data.system_message
        if self.data.system_message_placeholder:
            system_message = system_message.format_map(self.data.system_message_placeholder)
        return system(system_message)


    def translate_conversation_history(self):
        if not self.data.conversation_history:
            return []

        history_messages = list()
        for message in self.data.conversation_history:
            if message.get("role") in ["ai", "assistant"] and message.get("message"):
                history_messages.append(assistant(message.get("message")))
            elif message.get("role") in ["user", "human"] and message.get("message"):
                history_messages.append(user(message.get("message")))
            else:
                pass

        return history_messages


    async def get_messages(self):
        messages = [self.get_system_prompt()]
        if self.translate_conversation_history():
            messages.extend(self.translate_conversation_history())

        if not self.data.images:
            user_message = user(self.data.question)

        else:
            user_args = [self.data.question]
            async with httpx.AsyncClient() as httpx_client:
                for _image, _type in zip(self.data.images, self.data.image_types):
                    if _type == URL:
                        # TODO@jaehoon: 지원 외 content-type으로 response가 내려가는 url이면 에러가 남. 일단 어떤 이미지는 받을 수 있게 base64로 바꿔 진행. 불필요한 I/O 비용 추가니, 시간날 때마다 체크해볼 것
                        response = await httpx_client.get(_image)
                        image_bytes = response.content
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        detected_type = detect_image_format(image_bytes)
                        if detected_type:
                            media_type = f"image/{detected_type}"
                        else:
                            media_type = "image/jpeg"
                        image_url = f"data:{media_type};base64,{image_base64}"

                    else: # base64
                        detected_type = detect_image_format(_image)
                        if detected_type:
                            media_type = f"image/{detected_type}"
                        else:
                            media_type = "image/jpeg"
                        image_url = f"data:{media_type};base64,{_image}"

                    user_args.append(image(image_url=image_url, detail="high"))

            user_message = user(*[arg for arg in user_args])
            # user(
            #     "What are in these images?",
            #     image(image_url=f"data:image/jpeg;base64,{base64_image1}", detail="high"),
            #     image(image_url=f"data:image/jpeg;base64,{base64_image2}", detail="high")
            # )

        messages.append(user_message)
        return messages


    async def stream(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = await self.get_messages()
            model = self.data.model if not is_retry and self.data.model in XAI_MODEL_LIST else XAI_MODEL_LIST[0]

            chat = client.chat.create(model=model)
            for message in messages:
                chat.append(message)

            logging.info(f"session_key: {self.data.session_key} | [client.llm.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQEUST to xAI")

            is_first_res = True
            current_use_model = None
            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                async for response, chunk in chat.stream():
                    response_dict = make_response(0)
                    if not current_use_model and response and hasattr(response, "model"):
                        response_dict["vendor"] = XAI
                        response_dict["model"] = model
                    if response and hasattr(response, "outputs") and isinstance(response.outputs, dict) and response.outputs.get("finish_reason"):
                        response_dict["is_end"] = True
                    if chunk and isinstance(chunk, Chunk) and hasattr(chunk, "content"): # chunk엔 tool_calls, content(for streaming), reasoning_content, output(for chat) 등을 부를 수 있음
                        response_dict["text"] = chunk.content
                        if is_first_res:
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from xAI: {elapsed}")

                    # return result on streaming
                    if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                        result = serialize_response(response_dict)
                        yield result
                        await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.x.xAIClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.x.xAIClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def chat(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = await self.get_messages()
            model = self.data.model

            chat = client.chat.create(model=model)
            for message in messages:
                chat.append(message)

            logging.info(f"session_key: {self.data.session_key} | [client.x.xAIClient.chat] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to xAI")
            async with asyncio.timeout(300):
                response = await chat.sample()
                response_dict = make_response(iteration=0)
                response_dict["text"] = response.content
                response_dict["vendor"] = XAI
                response_dict["model"] = model
                response_dict["is_end"] = True
                #TODO@jaehoon: response_dict에 맞춰 데이터 내리는 코드 추가작업 필요
                return response_dict

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.x.xAIClient.chat] TIMEOUT ERROR: {300}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.x.xAIClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()


    async def stream_with_queue(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = await self.get_messages()
            model = self.data.model if not is_retry and self.data.model in XAI_MODEL_LIST else XAI_MODEL_LIST[0]

            chat = client.chat.create(model=model)
            for message in messages:
                chat.append(message)

            logging.info(f"session_key: {self.data.session_key} | [client.x.xAIClient.stream_with_queue] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to xAI")

            is_first_res = True
            async for response, chunk in chat.stream():
                response_dict = make_response(0)
                if is_first_res and response and hasattr(response, "model"):
                    response_dict["vendor"] = XAI
                    response_dict["model"] = model
                if response and hasattr(response, "outputs") and isinstance(response.outputs, dict) and response.outputs.get("finish_reason"):
                    response_dict["is_end"] = True
                if chunk and isinstance(chunk, Chunk) and hasattr(chunk, "content"):
                    response_dict["text"] = chunk.content
                    if is_first_res:
                        is_first_res = False
                        if not self.async_data.event.is_set():
                            self.async_data.event.set()
                        if self.data.time:
                            time_first_req = time()
                            elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                            logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from xAI: {elapsed}")

                if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                    result = serialize_response(response_dict)
                    await self.async_data.queue.put(result)
                    await asyncio.sleep(0)

            await self.async_data.queue.put(None)

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.x.xAIClient.stream_with_queue] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                result = make_error_response()
                await self.async_data.queue.put(result)
                await self.async_data.queue.put(None)
