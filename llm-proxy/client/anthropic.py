from anthropic import AsyncAnthropic
from anthropic.lib.streaming._types import TextEvent
from anthropic.lib.streaming import BetaMessageStopEvent
# from anthropic.lib.streaming._beta_types import BetaTextEvent, BetaContentBlockStopEvent, BetaThinkingEvent  # (원본 - 0.84.0에서 클래스명 변경됨)
from anthropic.lib.streaming._beta_types import ParsedBetaTextEvent as BetaTextEvent, ParsedBetaContentBlockStopEvent as BetaContentBlockStopEvent, BetaThinkingEvent
from anthropic.types.message_stop_event import MessageStopEvent
from anthropic.types.raw_message_start_event import RawMessageStartEvent
from anthropic.types.beta.beta_raw_message_start_event import BetaRawMessageStartEvent
from anthropic.types.beta.beta_raw_content_block_start_event import BetaRawContentBlockStartEvent
from anthropic._types import NOT_GIVEN
from anthropic.types.thinking_config_disabled_param import ThinkingConfigDisabledParam
from anthropic.types.thinking_config_enabled_param import ThinkingConfigEnabledParam

from client.common import *



@dataclass
class AnthropicClient:
    def __init__(self, data: ChatPayload | OcrChatPayload | ChatMCPPayload, async_data: AsyncData = None):
        self.data = data
        self.async_data = async_data
        self._api_key = self.get_api_key()


    def get_api_key(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return api_key


    def get_client(self):
        return AsyncAnthropic(api_key=self._api_key, timeout=360.0)


    def get_model(self, is_retry:bool):
        if is_retry and self.data.model in ANTHROPIC_FALLBACK_MODEL_OBJECT: # 재시도 + 요청한 모델이 베드락이면 매핑
            model = ANTHROPIC_FALLBACK_MODEL_OBJECT[self.data.model]
        else:
            model = self.data.model if self.data.model in ANTHROPIC_MODEL_LIST else ANTHROPIC_MODEL_LIST[0]
        return model


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
        """
        messages = [
            {"role": "user", "content": self.data.conversation_history if role == "human"}
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
            content = []
            # for image, _type, extension in zip(self.data.images, self.data.image_types, self.data.image_filename_extensions):
            for image, _type in zip(self.data.images, self.data.image_types):
                if _type == URL:
                    content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": image
                            },
                        }
                    )
                elif _type == BASE64:
                    pass
                    # content.append(
                    #     {
                    #         "type": "image",
                    #         "source": {
                    #             "type": "base64",
                    #             "media_type": f"image/{extension}",
                    #             "data": image
                    #         }
                    #     }
                    # )
                else:
                    pass
            content.append({"type": "text", "text": self.data.question})

        messages.append({"role": "user", "content": content})
        return messages


    # TODO@jaehoon: mcp_args, mcp_tools_args를 한번에 처리해 mcp_servers와 tools를 생성 -> 가능한 작은 인자로 받는 코드 고민
    # Agent -> Server + Token -> Tools: 트리구조로 이해하고 작업 시작
    # Agent: 1개
    # Server + Token: Agent 내 여러개
    # Tools: Server 내 여러개
    # 서비스 파트에서 이를 확인하고 설정할 수 있는 방안 고민하기
    # def make_mcp_args(self):
    #     try:
    #         pass
    #     except Exception as e:
    #         logging.warning(f"[client.anthropic.AnthropicClient.make_mcp_args] You need to check type of mcp_server: {type(self.data.mcp_server)}")
    #         return [
    #             {
    #                 "type": "url",
    #                 "url": os.getenv('MCP_SERVER_URL'),
    #                 "name": "knitlog_agent_server",
    #                 "authorization_token": "beusable-knitlog"
    #             }
    #         ]

    async def stream(self, is_retry: bool = False):
        try:
            system_prompt = self.get_system_prompt()
            client = self.get_client()
            messages = self.get_messages()
            model = self.get_model(is_retry=is_retry)
            thinking = ThinkingConfigDisabledParam(type="disabled") if self.data.service in KNITLOG_SERVICES else NOT_GIVEN

            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to ANTHROPIC")

            is_first_res = True
            async with asyncio.timeout(TIMEOUT) as timeout_cm:  # stream context 진입 타임아웃
                async with client.messages.stream(
                    model=model,
                    system=system_prompt,
                    max_tokens=50000 if "opus" not in model else 32000,
                    messages=messages,
                    thinking=thinking
                ) as response:
                    async for chunk in response:
                        response_dict = make_response(iteration=0)
                        if isinstance(chunk, TextEvent):
                            if is_first_res:
                                timeout_cm.reschedule(None)
                                is_first_res = False
                                if self.data.time:
                                    time_first_req = time()
                                    elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                    logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from ANTHROPIC: {elapsed}")
                            response_dict["text"] = chunk.text
                        elif isinstance(chunk, RawMessageStartEvent):
                            response_dict["model"] = chunk.message.model
                            response_dict["vendor"] = ANTHROPIC
                        elif isinstance(chunk, MessageStopEvent):
                            response_dict["is_end"] = True

                        if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end'], response_dict['thinking']]):
                            result = serialize_response(response_dict)
                            yield result
                            await asyncio.sleep(0)
        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def stream_with_mcp(self, is_retry: bool = False):
        mcp_clients = []  # 여러 클라이언트 관리
        tool_to_client_map = {}  # 도구 이름 -> 클라이언트 매핑

        try:
            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp_stdio] Starting MCP-enabled streaming")
            mcp_servers = list()
            mcp_tokens = list()
            if not self.data.mcp_info:
                # 단일 서버를 리스트로 변환
                mcp_servers.append(self.data.mcp_server or os.getenv("MCP_SERVER_URL"))
                mcp_tokens.append(self.data.mcp_token or getattr(self.data, "mcp_token", None))

                # 토큰이 없거나 개수가 부족하면 None으로 채우기
                if not mcp_tokens:
                    mcp_tokens = [None] * len(mcp_servers)
                elif len(mcp_tokens) < len(mcp_servers):
                    mcp_tokens.extend([None] * (len(mcp_servers) - len(mcp_tokens)))

                # mcp_allowed_tools 처리 (기존 호환성 유지)
                allowed_tools_config = self.data.mcp_allowed_tools

            else:
                allowed_tools_config = {}
                for mcp_info_each in self.data.mcp_info:
                    mcp_servers.append(mcp_info_each["uri"])
                    mcp_tokens.append(mcp_info_each.get("token", None))
                    allowed_tools_config[mcp_info_each["uri"]] = mcp_info_each["tools"]

            # 각 서버에 연결하고 도구 수집
            is_dict_config = isinstance(allowed_tools_config, dict)
            all_mcp_tools = []
            for server_idx, (server, token) in enumerate(zip(mcp_servers, mcp_tokens)):
                try:
                    logging.info(f"session_key: {self.data.session_key} | server: {server} | token: {token}")
                    mcp_client = await create_mcp_client(server, token, self.data.session_key)
                    mcp_clients.append(mcp_client)

                    tools = await mcp_client.list_tools()

                    # 서버별 허용 도구 필터링
                    server_allowed_tools = None
                    if allowed_tools_config:
                        if is_dict_config:
                            if isinstance(allowed_tools_config, dict):
                                server_allowed_tools = allowed_tools_config.get(server)
                        else:
                            if isinstance(allowed_tools_config, list):
                                server_allowed_tools = allowed_tools_config

                    # 서버 prefix 생성
                    server_prefix = f"mcp{server_idx}"

                    # 도구 이름 -> 클라이언트 매핑 저장
                    filtered_count = 0
                    for tool in tools:
                        original_tool_name = tool.get("name")

                        # 허용 도구 필터링
                        if server_allowed_tools and original_tool_name not in server_allowed_tools:
                            continue

                        # prefix 추가한 도구명 생성
                        prefixed_tool_name = f"{server_prefix}__{original_tool_name}"

                        # 매핑 저장 (prefix된 이름 -> 클라이언트)
                        tool_to_client_map[prefixed_tool_name] = mcp_client

                        # Anthropic에 전달할 도구 정보 (prefix된 이름 사용)
                        prefixed_tool = tool.copy()
                        prefixed_tool["name"] = prefixed_tool_name
                        original_desc = tool.get("description", "")
                        prefixed_tool["description"] = f"[Server: {server}] {original_desc}"

                        all_mcp_tools.append(prefixed_tool)
                        filtered_count += 1

                    logging.info(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] Connected to {server} (prefix: {server_prefix}), found {len(tools)} tools, filtered to {filtered_count} tools")
                except Exception as e:
                    logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] Failed to connect to {server}: {e}")
                    continue

            if not mcp_clients:
                logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] There is no mcp_clients")
                raise Exception("Failed to connect to any MCP server")

            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] Total {len(mcp_clients)} servers connected, {len(all_mcp_tools)} tools available")

            # Anthropic 클라이언트 및 파라미터 설정
            client = self.get_client()
            system_prompt = self.get_system_prompt()
            messages = self.get_messages()
            model = self.get_model(is_retry=is_retry)
            tools = self.translate_mcp_tools_to_anthropic_format(all_mcp_tools)

            iteration = 0
            max_iterations = 10
            is_first_res = True
            tool_list = list()

            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp_stdio] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to ANTHROPIC MCP STDIO")

            while iteration < max_iterations:
                logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp_stdio] Iteration: {iteration}")

                # 안전장치: max_iter에 도달하면 tools 없이 최종 답변 요청
                current_tools = tools if iteration < max_iterations - 1 else NOT_GIVEN

                # 응답 처리 변수
                tool_uses = []
                assistant_content = []
                current_text = ""
                timeout_cancelled = False  # 각 iteration마다 초기화

                async with asyncio.timeout(TIMEOUT) as timeout_cm:
                    async with client.beta.messages.stream(
                            model=model,
                            max_tokens=50000 if "opus" not in model else 32000,
                            system=system_prompt,
                            messages=messages,
                            tools=current_tools,
                            thinking=ThinkingConfigEnabledParam(type="enabled", budget_tokens=4000),
                    ) as response:
                        async for chunk in response:
                            response_dict = make_response(iteration)

                            # 이벤트 시작 감지
                            if isinstance(chunk, BetaRawMessageStartEvent):
                                if hasattr(chunk, "message") and hasattr(chunk.message, "model") and chunk.message.model:
                                    response_dict["model"] = chunk.message.model
                                    response_dict["vendor"] = ANTHROPIC
                                    if not timeout_cancelled:
                                        timeout_cancelled = True
                                        timeout_cm.reschedule(None)
                                    if is_first_res:
                                        is_first_res = False
                                        if self.data.time:
                                            time_first_req = time()
                                            elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                            logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from ANTHROPIC MCP STDIO: {elapsed}, Iteration of ANTHROPIC MCP STDIO: {iteration}")

                            # 텍스트 스트리밍
                            elif isinstance(chunk, BetaTextEvent) and hasattr(chunk, 'text') and chunk.text:
                                if not timeout_cancelled:
                                    timeout_cancelled = True
                                    timeout_cm.reschedule(None)
                                if is_first_res:
                                    is_first_res = False
                                    if self.data.time:
                                        time_first_req = time()
                                        elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                        logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from ANTHROPIC MCP STDIO: {elapsed}, Iteration of ANTHROPIC MCP STDIO: {iteration}")
                                current_text += chunk.text
                                response_dict["text"] = chunk.text

                            # Thinking 스트리밍
                            elif isinstance(chunk, BetaThinkingEvent) and hasattr(chunk, 'thinking') and chunk.thinking:
                                if not timeout_cancelled:
                                    timeout_cancelled = True
                                    timeout_cm.reschedule(None)
                                if is_first_res:
                                    is_first_res = False
                                    if self.data.time:
                                        time_first_req = time()
                                        elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                        logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from ANTHROPIC MCP STDIO: {elapsed}, Iteration of ANTHROPIC MCP STDIO: {iteration}")
                                response_dict["thinking"] = chunk.thinking

                            # Content block 시작 (tool_use 감지)
                            elif isinstance(chunk, BetaRawContentBlockStartEvent):
                                if hasattr(chunk, "content_block"):
                                    block = chunk.content_block
                                    if hasattr(block, "type") and block.type == "tool_use":
                                        tool_uses.append({
                                            "id": block.id,
                                            "name": block.name,
                                            "input": {}
                                        })
                                        tool_list.append(block.name)
                                        logging.info(f"session_key: {self.data.session_key} | [tool_list] {block.name} is appended. Current tool list is {tool_list}")

                            # Content block 종료 (tool_use 완성)
                            elif isinstance(chunk, BetaContentBlockStopEvent):
                                if hasattr(chunk, "content_block"):
                                    block = chunk.content_block
                                    if hasattr(block, "type") and block.type == "tool_use":
                                        response_dict["text"] = "\n\n\n"
                                        response_dict["tool_name"] = block.name
                                        response_dict["tool_text"] = str(block.input) if hasattr(block, "input") else ""
                                        # tool_uses의 input 업데이트
                                        for tu in tool_uses:
                                            if tu["id"] == block.id:
                                                tu["input"] = block.input if hasattr(block, "input") else {}
                                                break

                            # 메시지 종료
                            elif isinstance(chunk, BetaMessageStopEvent):
                                # stop_reason 확인은 stream 객체에서
                                pass

                            if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end'], response_dict['thinking']]):
                                yield serialize_response(response_dict)
                                await asyncio.sleep(0)

                        # stream 종료 후 stop_reason 확인
                        final_message = await response.get_final_message()
                        stop_reason = final_message.stop_reason

                # 도구 사용이 없으면 종료
                if stop_reason != "tool_use" or not tool_uses:
                    logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp_stdio] No tool use detected (stop_reason: {stop_reason}). Finishing.")
                    response_dict = make_response(iteration)
                    response_dict["is_end"] = True
                    yield serialize_response(response_dict)
                    break

                # assistant content 구성
                if current_text:
                    assistant_content.append({"type": "text", "text": current_text})

                logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp_stdio] Executing {len(tool_uses)} tools")
                tool_results = []

                for tool_use in tool_uses:
                    prefixed_tool_name = tool_use.get("name")
                    tool_input = tool_use.get("input")
                    tool_id = tool_use.get("id")

                    if isinstance(tool_input, str):
                        try:
                            tool_input = json.loads(tool_input)
                        except json.JSONDecodeError as e:
                            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] Failed to parse tool input: {e}")
                            tool_input = {}

                    # 해당 도구를 제공하는 MCP 클라이언트 찾기
                    target_mcp_client = tool_to_client_map.get(prefixed_tool_name)
                    if not target_mcp_client:
                        logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] No client found for tool: {prefixed_tool_name}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: Tool {prefixed_tool_name} not found",
                            "is_error": True
                        })
                        continue

                    # prefix 제거하여 원래 도구명 추출
                    if "__" in prefixed_tool_name:
                        original_tool_name = prefixed_tool_name.split("__", 1)[1]
                    else:
                        original_tool_name = prefixed_tool_name

                    # MCP 서버에서 도구 실행
                    try:
                        result = await target_mcp_client.call_tool(original_tool_name, tool_input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": str(result)
                        })
                        assistant_content.append({
                            "type": "tool_use",
                            "id": tool_id,
                            "name": prefixed_tool_name,
                            "input": tool_input
                        })
                    except Exception as e:
                        logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp_stdio] Tool execution error: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })

                # 툴 결과물 추출 후!
                response_dict = make_response(iteration)
                response_dict["assistant_content"] = assistant_content
                response_dict["tool_results"] = tool_results
                if any([response_dict['assistant_content'], response_dict['tool_results']]):
                    yield serialize_response(response_dict)

                # 다음 iteration을 위해 messages 업데이트
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                iteration += 1

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_mcp] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        finally:
            # 모든 MCP 클라이언트 연결 종료
            for mcp_client in mcp_clients:
                try:
                    await mcp_client.disconnect()
                    logging.info(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp] MCP client disconnected")
                except Exception as e:
                    logging.error(f"session_key: {self.data.session_key} | [client.anthropic.stream_with_mcp] Error disconnecting MCP client: {e}")


    async def chat(self, is_retry: bool = False):
        try:
            system_prompt = self.get_system_prompt()
            client = self.get_client()
            messages = self.get_messages()
            model = self.get_model(is_retry=is_retry)
            thinking = ThinkingConfigDisabledParam(type="disabled") if self.data.service in KNITLOG_SERVICES else NOT_GIVEN

            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to ANTHROPIC")

            response = await client.messages.create(
                    model=model,
                    system=system_prompt,
                    max_tokens=21_000 if "opus" not in model else 16_000,
                    messages=messages,
                    thinking=thinking,
                    stream=False
            )

            response_dict = make_response(iteration=0)
            response_dict["text"] = response.content[0].text
            response_dict["vendor"] = ANTHROPIC
            response_dict["model"] = response.model
            response_dict["is_end"] = True
            return response_dict

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()


    async def stream_with_queue(self, is_retry: bool = False):
        try:
            system_prompt = self.get_system_prompt()
            client = self.get_client()
            messages = self.get_messages()
            model = self.get_model(is_retry=is_retry)
            thinking = ThinkingConfigDisabledParam(type="disabled") if self.data.service in KNITLOG_SERVICES else NOT_GIVEN

            logging.info(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_queue] service: {self.data.service} | model: {model} | is_retry: {is_retry} | REQUEST to ANTHROPIC")

            is_first_res = True
            async with client.messages.stream(
                model=model,
                system=system_prompt,
                max_tokens=50000 if "opus" not in model else 32000,
                messages=messages,
                thinking=thinking
            ) as response:
                async for chunk in response:
                    response_dict = make_response(iteration=0)
                    if isinstance(chunk, TextEvent):
                        if is_first_res:
                            is_first_res = False
                            if not self.async_data.event.is_set():
                                self.async_data.event.set()
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from ANTHROPIC: {elapsed}")
                        response_dict["text"] = chunk.text
                    elif isinstance(chunk, RawMessageStartEvent):
                        response_dict["model"] = chunk.message.model
                        response_dict["vendor"] = ANTHROPIC
                    elif isinstance(chunk, MessageStopEvent):
                        response_dict["is_end"] = True

                    if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end'], response_dict['thinking']]):
                        result = serialize_response(response_dict)
                        await self.async_data.queue.put(result)
                        await asyncio.sleep(0)

            await self.async_data.queue.put(None)

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.anthropic.AnthropicClient.stream_with_queue] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                result = make_error_response()
                await self.async_data.queue.put(result)
                await self.async_data.queue.put(None)


    def translate_mcp_tools_to_anthropic_format(self, mcp_tools: list[dict]) -> list[dict]:
        """MCP 도구를 Anthropic 형식으로 변환"""
        anthropic_tools = []
        for tool in mcp_tools:
            anthropic_tools.append({
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "input_schema": tool.get("input_schema", {})
            })
        return anthropic_tools
