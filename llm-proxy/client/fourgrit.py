import openai

from client.common import *



class FourgritClient:
    def __init__(self, data: ChatPayload | OcrChatPayload | ChatMCPPayload | EmbeddingsPayload, async_data: AsyncData = None):
        self.data = data
        self.fourgrit_url = os.getenv("FOURGRIT_URL")
        self.async_data = async_data
        self._client = None


    def get_client(self):
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                base_url=self.fourgrit_url,
                api_key="fourgrit-llm-key"
            )
        return self._client


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
            {"role": "user", "content": self.data.conversation_history if role == "human"}
            {"role": "assistant", "content": self.data.conversation_history if role == "ai"},
        ]
        """
        messages = [
            {"role": "user", "content": "You are a helpful assistant! describe what you should do"},
            {"role": "assistant", "content": self.get_system_prompt()}
        ]
        history_messages = self.translate_conversation_history()
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": self.data.question})
        return messages


    async def translate_tools_for_function_call(self):
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
            server_stage = os.getenv("SERVER_STAGE")
            if server_stage in [DOCKER_LOCAL, DOCKER]:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url=os.getenv("FOURGRIT_EMBEDDING_URL"),
                        json={
                            "texts": self.data.text
                        }
                    )
                response_data = response.json()
                if isinstance(self.data.text, list):
                    vector = list()
                    for v in response_data:
                        np_vector = np.array(v, dtype=np.float32)
                        base64_vector = base64.b64encode(np_vector.tobytes()).decode('utf-8')
                        vector.append(base64_vector)
                else:
                    np_vector = np.array(response_data, dtype=np.float32)
                    base64_vector = base64.b64encode(np_vector.tobytes()).decode('utf-8')
                    vector = base64_vector
                return vector

            else:
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
            logging.error(f"session_key: {self.data.session_key} | [client.llm.embeddings] ERROR: {e}")
            raise FirstTryError() if not is_retry else SecondTryError()


    async def chat(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = self.get_messages()

            response = await client.chat.completions.create(
                model=self.data.model,
                messages=messages,
                temperature=self.data.temperature or DEFAULT_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.llm.chat] ERROR: {e}")
            raise FirstTryError() if not is_retry else SecondTryError()


    async def stream(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = self.get_messages()

            logging.info(f"session_key: {self.data.session_key} | [client.llm.stream] REQUEST to fourgrit")
            logging.info(f"session_key: {self.data.session_key} | [client.llm.stream] Address: {self.fourgrit_url}")
            args = {
                # "model": "google/gemma-3-12b-it",
                "model": "openai/gpt-oss-20b",
                "messages": messages,
                "stream": True,
            }

            if self.data.model not in OPENAI_REASONING_MODEL_LIST:
                args["temperature"] = self.data.temperature or DEFAULT_TEMPERATURE
            else:
                args["reasoning_effort"] = "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"

            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                response = await client.chat.completions.create(**args)
                is_first_res = True
                async for chunk in response:
                    response_dict = make_response(iteration=0) # {"iteration": iteration, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                    if not chunk.choices or chunk.choices[0].delta.content is None:
                        continue
                    if is_first_res:
                        response_dict["model"] = chunk.model if hasattr(chunk, "model") else ""
                        response_dict["vendor"] = FOURGRIT
                        is_first_res = False
                        timeout_cm.reschedule(None)
                        if self.data.time:
                            time_first_req = time()
                            elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                            logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from FOURGRIT: {elapsed}")
                    if hasattr(chunk, "choices") and isinstance(chunk.choices, (list, tuple)) and chunk.choices and hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                        response_dict["text"] = chunk.choices[0].delta.content
                    if hasattr(chunk, "choices") and isinstance(chunk.choices, (list, tuple)) and chunk.choices and hasattr(chunk.choices[0], "finish_reason") and chunk.choices[0].finish_reason:
                        response_dict["is_end"] = True

                    if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end']]):
                        result = serialize_response(response_dict)
                        yield result
                        await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    def translate_mcp_tools_to_openai_format(self, mcp_tools: list[dict]):
        """MCP 도구 목록을 OpenAI API 형식으로 변환"""
        allowed_tools = ["get_current_time", "query_prescription_data"]

        openai_tools = []
        for tool in mcp_tools:
            tool_name = tool.get("name")
            if tool_name in allowed_tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool.get("description", ""),
                        "parameters": tool.get("input_schema", {})
                    }
                })
        return openai_tools


    async def stream_with_mcp(self, is_retry: bool = False):
        mcp_client = None
        try:
            logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Starting MCP-enabled streaming")
            mcp_client = await create_mcp_client(os.getenv("MCP_SERVER_URL"), getattr(self.data, 'mcp_token', None))
            mcp_tools = await mcp_client.list_tools()
            openai_tools = self.translate_mcp_tools_to_openai_format(mcp_tools)

            # 초기 메시지 구성
            client = await self.get_client()
            messages = self.get_messages()
            iteration = 0
            max_iterations = 10
            tool_list = []
            while iteration <= max_iterations:
                logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Iteration {iteration}")

                # API 요청 인자 구성
                args = {
                    # "model": "gpt-oss-20b",
                    "model": "google/gemma-3-27b",
                    "messages": messages,
                    "stream": True,
                }

                # Tool 제공 로직: max_iter 도달 전까지는 항상 tool 제공
                if iteration < max_iterations and openai_tools:
                    args["tools"] = openai_tools
                    args["tool_choice"] = "auto"
                else:
                    # Max iteration 도달 시 tool 제거하고 강제로 답변 생성
                    if iteration == max_iterations:
                        logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Max iterations reached. Requesting final answer without tools.")
                        if messages and messages[-1]["role"] == "tool":
                            messages.append({
                                "role": "user",
                                "content": "위의 도구 실행 결과를 바탕으로 사용자의 원래 질문에 대한 최종 답변을 자연스러운 문장으로 작성해주세요."
                            })

                # 스트리밍 요청
                async with asyncio.timeout(TIMEOUT) as timeout_cm:
                    response = await client.chat.completions.create(**args)

                    is_first_res = True
                    tool_calls_dict = {}
                    assistant_message_content = ""
                    reasoning_message = ""
                    async for chunk in response:
                        response_dict = make_response(iteration) # {"iteration": iteration, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                        if is_first_res:
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from FOURGRIT MCP: {elapsed}")
                            if hasattr(chunk, "model"):
                                response_dict["model"] = chunk.model
                                response_dict["vendor"] = FOURGRIT

                        delta = chunk.choices[0].delta

                        if hasattr(delta, "content") and delta.content:
                            assistant_message_content += delta.content
                            response_dict["text"] = delta.content
                        if hasattr(delta, "reasoning") and delta.reasoning:
                            assistant_message_content += delta.reasoning
                            reasoning_message += delta.reasoning

                        # Tool calls 수집
                        if delta.tool_calls:
                            for tool_call_chunk in delta.tool_calls:
                                if hasattr(tool_call_chunk, "index") and hasattr(tool_call_chunk, "id") and hasattr(tool_call_chunk, "function") and hasattr(tool_call_chunk.function, "name") and tool_call_chunk.index not in tool_calls_dict:
                                    idx = tool_call_chunk.index
                                    tool_calls_dict[idx] = {
                                        "id": tool_call_chunk.id or "",
                                        "type": "function",
                                        "function": {
                                            "name": tool_call_chunk.function.name or "",
                                            "arguments": ""
                                        }
                                    }

                                    # 함수 이름 업데이트
                                    if tool_call_chunk.function.name:
                                        tool_calls_dict[idx]["function"]["name"] = tool_call_chunk.function.name

                                    # 인자 누적
                                    if tool_call_chunk.function.arguments:
                                        tool_calls_dict[idx]["function"]["arguments"] += tool_call_chunk.function.arguments

                        result = serialize_response(response_dict)
                        yield result
                        await asyncio.sleep(0)

                        # 스트림 종료 확인
                        if chunk.choices[0].finish_reason:
                            break

                # Tool calls가 없으면 최종 답변이므로 while 루프 종료
                if not tool_calls_dict:
                    logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] No tool use detected. Finishing.")
                    response_dict = make_response(iteration) # {"iteration": iteration, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                    response_dict["is_end"] = True
                    result = serialize_response(response_dict)
                    yield result
                    await asyncio.sleep(0)

                # Tool calls 실행
                tool_calls = list(tool_calls_dict.values())
                logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Executing {len(tool_calls)} tools")
                logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Tool calls structure: {json.dumps(tool_calls, indent=2)}")

                # Assistant 메시지 추가 (tool_calls 포함)
                assistant_msg = {
                    "role": "assistant",
                    "content": assistant_message_content or None,
                    "tool_calls": tool_calls
                }
                messages.append(assistant_msg)
                logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Added assistant message with tool_calls")

                # 각 tool call 실행 및 결과 수집
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_id = tool_call["id"]
                    tool_list.append(tool_name)

                    # 도구 사용 알림 전송
                    arguments_str = None
                    try:
                        arguments_str = tool_call["function"]["arguments"]
                        tool_input = json.loads(arguments_str) if arguments_str else {}
                    except json.JSONDecodeError as e:
                        logging.error(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Failed to parse tool arguments: {e}")
                        tool_input = {}

                    # response_shape = {"iteration": iteration, "text": "\n\n\n", "model": None, "vendor": None, "tool_name": tool_name, "tool_text": arguments_str, "is_end": False}
                    response_dict = make_response(iteration)
                    response_dict["text"] = "\n\n\n"
                    response_dict["tool_name"] = tool_name
                    response_dict["tool_text"] = arguments_str
                    result = serialize_response(response_dict)
                    yield result
                    await asyncio.sleep(0)

                    # MCP 서버에서 도구 실행
                    try:
                        result = await mcp_client.call_tool(tool_name, tool_input)
                        tool_result_content = str(result)
                        logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Tool '{tool_name}' executed successfully. Result: {tool_result_content[:200]}")
                    except Exception as e:
                        tool_result_content = f"Error: {str(e)}"
                        logging.error(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Tool execution error: {e}")

                    # Tool 결과를 메시지에 추가
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": tool_result_content
                    }
                    messages.append(tool_msg)
                    logging.info(f"session_key: {self.data.session_key} | tool_msg: {tool_msg}")
                    logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Added tool result message for '{tool_name}'")

                    iteration += 1

                logging.info(f"session_key: {self.data.session_key} | [tool_list] Current tool list is {tool_list}")
                logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Messages array now has {len(messages)} messages. Last 3 roles: {[m['role'] for m in messages[-3:]]}")

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        finally:
            # MCP 연결 종료
            if mcp_client:
                try:
                    await mcp_client.disconnect()
                    logging.info(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] MCP client disconnected")
                except Exception as e:
                    logging.error(f"session_key: {self.data.session_key} | [client.local.stream_with_mcp] Error disconnecting MCP client: {e}")


    async def stream_with_queue(self, is_retry: bool = False):
        try:
            client = self.get_client()
            messages = self.get_messages()

            logging.info(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream_with_queue] service: {self.data.service} | is_retry: {is_retry} | REQUEST to fourgrit")
            args = {
                "model": "openai/gpt-oss-20b",
                "messages": messages,
                "stream": True,
            }
            if self.data.model not in OPENAI_REASONING_MODEL_LIST:
                args["temperature"] = self.data.temperature or DEFAULT_TEMPERATURE
            else:
                args["reasoning_effort"] = "medium" if self.data.service in ["reportchat", "baAIReport"] else "low"

            response = await client.chat.completions.create(**args)

            is_first_res = True
            async for chunk in response:
                if not chunk.choices or chunk.choices[0].delta.content is None:
                    continue

                response_dict = make_response(iteration=0)
                if is_first_res:
                    response_dict["model"] = chunk.model if hasattr(chunk, "model") else ""
                    response_dict["vendor"] = FOURGRIT
                    is_first_res = False
                    if not self.async_data.event.is_set():
                        self.async_data.event.set()
                    if self.data.time:
                        time_first_req = time()
                        elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                        logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from FOURGRIT: {elapsed}")

                response_dict["text"] = chunk.choices[0].delta.content
                if chunk.choices[0].finish_reason:
                    response_dict["is_end"] = True

                result = serialize_response(response_dict)
                await self.async_data.queue.put(result)
                await asyncio.sleep(0)

            await self.async_data.queue.put(None)

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.fourgrit.FourgritClient.stream_with_queue] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                result = make_error_response()
                await self.async_data.queue.put(result)
                await self.async_data.queue.put(None)
