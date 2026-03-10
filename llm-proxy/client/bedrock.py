from pathlib import Path

import httpx

import aioboto3
from botocore.config import Config

from client.common import *



@dataclass
class Boto3Session:
    _async_session = None

    def get_async_session(self):
        if self._async_session is None:
            return aioboto3.Session()
        else:
            return self._async_session



@dataclass
class BedrockClient(Boto3Session):
    data: ChatPayload | OcrChatPayload | ChatMCPPayload
    async_data: AsyncData = None
    region: str = os.getenv("AWS_DEFAULT_REGION")


    def get_async_client(self):
        """context manager 반환"""
        session = self.get_async_session()
        return session.client(
            'bedrock-runtime',
            config=Config(read_timeout=360,
                          connect_timeout=360
            )
        )


    def get_provider(self):
        if "anthropic" in self.data.model or self.data.model in ANTHROPIC_MODEL_LIST:
            return ANTHROPIC
        elif "meta" in self.data.model:
            return META
        else:
            return BEDROCK


    def get_model(self, is_retry:bool):
        if is_retry and self.data.model in BEDROCK_FALLBACK_MODEL_OBJECT: # 재시도 + 요청한 모델이 앤트로픽이면 매핑
            model = BEDROCK_FALLBACK_MODEL_OBJECT[self.data.model]
        else:
            model = self.data.model if self.data.model in BEDROCK_MODEL_LIST else BEDROCK_MODEL_LIST[0]
        return model


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


    async def get_messages(self):
        """
        messages = [
            {"role": "developer", "content": await self.get_system_prompt()},
            {"role": "user", "content": self.data.conversation_history if role == "human"}
            {"role": "assistant", "content": self.data.conversation_history if role == "ai"},
        ]
        """
        messages = [{"role": "assistant", "content": self.get_system_prompt() or "-"}]
        history_messages = self.translate_conversation_history()
        if history_messages:
            messages.extend(history_messages)

        # 마지막 사용자 메시지
        if not self.data.images:
            content = self.data.question
        else:
            content = []
            async with httpx.AsyncClient() as client:
                # for image, _type, extension in zip(self.data.images, self.data.image_types, self.data.image_filename_extensions):
                for image, _type in zip(self.data.images, self.data.image_types):
                    if _type == URL:
                        # TODO@jaehoon: 지원 외 content-type으로 response가 내려가는 url이면 에러가 남. 일단 어떤 이미지는 받을 수 있게 base64로 바꿔 진행. 불필요한 I/O 비용 추가니, 시간날 때마다 체크해볼 것
                        response = await client.get(image)
                        image_bytes = response.content
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        detected_type = detect_image_format(image_bytes)
                        if detected_type:
                            media_type = f"image/{detected_type}"
                        else:
                            media_type = "image/jpeg"

                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        })
                    elif _type == BASE64:
                        pass
                        # content.append({
                        #     "type": "image",
                        #     "source": {
                        #         "type": "base64",
                        #         "media_type": f"image/{extension}",
                        #         "data": image
                        #     }
                        # })

            content.append({"type": "text", "text": self.data.question})

        messages.append({"role": "user", "content": content})
        return messages


    async def get_body(self, is_function_call:bool=None, is_mcp:bool=None, mcp_tools:list[dict]=None):
        """
        :param is_function_call:
        :param is_mcp:
        :param mcp_tools: 만약 is_mcp가 True이면 반드시 mcp_tools를 list_tools로 가져와야함
        :return:
        """
        if self.get_provider() == ANTHROPIC or is_mcp:
            system_prompt = self.get_system_prompt()
            messages = await self.get_messages()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "system": system_prompt,
                "messages": messages,
                "max_tokens": 50000
            }
            if is_mcp and mcp_tools:
                body["tools"] = self.translate_mcp_tools_to_bedrock_format(mcp_tools)
                body["tool_choice"] = {"type": "auto"}
                body["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": 4000
                }
                logging.info(f"session_key: {self.data.session_key} | [client.bedrock.get_body] Tools allowed is {len(body['tools'])}")
            elif is_function_call:
                body["tools"] = self.translate_tools_for_function_call()
                body["tool_choice"] = {"type": "auto"}
            elif not is_mcp and not mcp_tools and self.data.model != BEDROCK_MODEL_LIST[0]:
                body["temperature"] = 0
        else:
            # meta나 다른 vendor를 쓰려면 추가 작업 필요
            body = {}
        return json.dumps(body)


    def translate_mcp_tools_to_bedrock_format(self, mcp_tools:list[dict] = None):
        """
        MCP 도구를 Bedrock 형식으로 변환
        주의: stream_with_mcp에서 이미 필터링된 도구만 전달되므로 추가 필터링 불필요
        """
        bedrock_tools = []
        for tool in mcp_tools:
            bedrock_tools.append({
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "input_schema": tool.get("input_schema", {})
            })
        return bedrock_tools


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
            body = await self.get_body()
            modelId = self.get_model(is_retry=is_retry)
            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream] service: {self.data.service} | model: {modelId} | is_retry: {is_retry} | REQUEST to BEDROCK")

            async with asyncio.timeout(TIMEOUT) as timeout_cm:
                async with self.get_async_client() as client:
                    response = await client.invoke_model_with_response_stream(
                        modelId=modelId,
                        body=body,
                        contentType='application/json',
                        accept="application/json"
                    )

                    is_first_res = True
                    async for event in response['body']:
                        response_dict = make_response(iteration=0) # {"iteration": iteration, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                        bytes_data = event.get("chunk", {}).get("bytes", b"")
                        if not bytes_data:
                            continue
                        data = json.loads(bytes_data.decode('utf-8'))
                        if is_first_res and data.get("type") == "message_start":
                            is_first_res = False
                            timeout_cm.reschedule(None)
                            response_dict["model"] = data.get("message", {"model": ""}).get("model", "")
                            response_dict["vendor"] = BEDROCK
                            if self.data.time:
                                time_first_req = time()
                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from BEDROCK: {elapsed}")
                        if data.get("type") == "content_block_delta":
                            response_dict["text"] = data.get("delta", {"text": ""}).get("text", "")
                        if data.get("type") == "message_stop":
                            response_dict["is_end"] = True

                        if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end'], response_dict['thinking']]):
                            result = serialize_response(response_dict)
                            yield result
                            await asyncio.sleep(0)

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()


    async def stream_with_mcp(self, is_retry: bool = False):
        mcp_clients = []  # 여러 클라이언트 관리
        tool_to_client_map = {}  # 도구 이름 -> 클라이언트 매핑

        try:
            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Starting MCP-enabled streaming")
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
                    client = await create_mcp_client(server, token, self.data.session_key)
                    mcp_clients.append(client)

                    tools = await client.list_tools()

                    # 서버별 허용 도구 필터링
                    server_allowed_tools = None
                    if allowed_tools_config:
                        if is_dict_config:
                            # 새 방식: 서버별 구분 (dict 타입 확정)
                            if isinstance(allowed_tools_config, dict):
                                server_allowed_tools = allowed_tools_config.get(server)
                        else:
                            # 기존 방식: 모든 서버에 동일 적용 (list 타입 확정)
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
                        tool_to_client_map[prefixed_tool_name] = client

                        # Bedrock에 전달할 도구 정보 (prefix된 이름 사용)
                        prefixed_tool = tool.copy()
                        prefixed_tool["name"] = prefixed_tool_name
                        # description에 서버 정보 추가
                        original_desc = tool.get("description", "")
                        prefixed_tool["description"] = f"[Server: {server}] {original_desc}"

                        all_mcp_tools.append(prefixed_tool)
                        filtered_count += 1

                    logging.info(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] Connected to {server} (prefix: {server_prefix}), found {len(tools)} tools, filtered to {filtered_count} tools")
                except Exception as e:
                    logging.error(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] Failed to connect to {server}: {e}")
                    continue

            if not mcp_clients:
                logging.error(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] There is not mcp_clients")
                raise Exception("Failed to connect to any MCP server")

            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] Total {len(mcp_clients)} servers connected, {len(all_mcp_tools)} tools available")

            body = await self.get_body(is_mcp=True, mcp_tools=all_mcp_tools)
            body_dict = json.loads(body)
            messages = body_dict["messages"]# 대화이력 적용
            modelId = self.get_model(is_retry=is_retry)

            iteration = 0
            max_iterations = 10 # should be > 3
            is_first_res = True
            tool_list = list()

            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] service: {self.data.service} | model: {modelId} | is_retry: {is_retry} | REQUEST to BEDROCK MCP")

            async with self.get_async_client() as client:
                while iteration <= max_iterations:
                    logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Iteration: {iteration}")

                    # 안전장치: 만약 max_iter 넘어서까지 tool이 나온다면? 툴 빼서 답변하도록!
                    if iteration == max_iterations:
                        body_dict.pop("tools", None)
                        body_dict.pop("tool_choice", None)
                        if messages and messages[-1]["role"] == "user":
                            last_content = messages[-1]["content"]
                            if isinstance(last_content, list):
                                last_content.append({
                                    "type": "text",
                                    "text": "위의 도구 실행 결과를 바탕으로 사용자의 원래 질문에 대한 최종 답변을 자연스러운 문장으로 작성해주세요."
                                })
                        body_dict["messages"] = messages
                        logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Max iterations reached. Requesting final answer without tools.")

                    timeout_cancelled = False  # 각 iteration마다 초기화
                    async with asyncio.timeout(TIMEOUT) as timeout_cm:
                        response = await client.invoke_model_with_response_stream(
                            modelId=modelId,
                            body=body,
                            contentType='application/json',
                            accept="application/json"
                        )

                        # 응답 처리
                        tool_uses = []
                        assistant_content = []
                        current_thinking = None  # thinking 블록 추적용
                        current_text = ""  # text 블록 누적용
                        async for event in response['body']:
                            response_dict = make_response(iteration) # {"iteration": iteration, "text": None, "model": None, "vendor": None, "tool_name": None, "tool_text": None, "is_end": False}
                            bytes_data = event.get("chunk", {}).get("bytes", b"")
                            if not bytes_data:
                                continue
                            data = json.loads(bytes_data.decode('utf-8'))

                            # 메세지 시작 감지!
                            if data.get("type") == "message_start":
                                if not timeout_cancelled:
                                    timeout_cancelled = True
                                    timeout_cm.reschedule(None)
                                if is_first_res:
                                    is_first_res = False
                                    if self.data.time:
                                        time_first_req = time()
                                        elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                        logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from BEDROCK MCP_STDIO: {elapsed}, Iteration of BEDROCK MCP STDIO: {iteration}")
                                if data.get("message") and data["message"].get("model"):
                                    response_dict["model"] = data["message"]["model"]
                                    response_dict["vendor"] = BEDROCK

                            # 텍스트 스트리밍!
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})

                                # Text delta 처리 (누적하고 나중에 한 번에 추가)
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        current_text += text
                                        response_dict["text"] = text
                                        if not timeout_cancelled:
                                            timeout_cancelled = True
                                            timeout_cm.reschedule(None)
                                        if is_first_res:
                                            is_first_res = False
                                            if self.data.time:
                                                time_first_req = time()
                                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from BEDROCK MCP_STDIO: {elapsed}, Iteration of BEDROCK MCP STDIO: {iteration}")

                                # Thinking Message 처리
                                if delta.get("type") == "thinking_delta":
                                    thinking_text = delta.get("thinking", "")
                                    if thinking_text:
                                        response_dict["thinking"] = thinking_text
                                        if current_thinking is not None:
                                            current_thinking["thinking"] += thinking_text
                                        if not timeout_cancelled:
                                            timeout_cancelled = True
                                            timeout_cm.reschedule(None)
                                        if is_first_res:
                                            is_first_res = False
                                            if self.data.time:
                                                time_first_req = time()
                                                elapsed = timedelta(seconds=int(time_first_req - self.data.time))
                                                logging.info(f"session_key: {self.data.session_key} | [TIMETEST] ⏱️ TIME from BEDROCK MCP_STDIO: {elapsed}, Iteration of BEDROCK MCP STDIO: {iteration}")

                                # Signature delta 처리 (thinking 블록의 서명)
                                if delta.get("type") == "signature_delta" and current_thinking is not None:
                                    signature = delta.get("signature", "")
                                    if signature:
                                        current_thinking["signature"] += signature

                            # Thinking 블록 감지 (extended thinking 활성화 시)
                            if data.get("type") == "content_block_start":
                                block = data.get("content_block", {})
                                if block.get("type") == "thinking":
                                    current_thinking = {"type": "thinking", "thinking": "", "signature": ""}
                                    assistant_content.append(current_thinking)
                                    logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Thinking block started")

                            # Tool use 감지
                            if data.get("type") == "content_block_start":
                                block = data.get("content_block", {})
                                if block.get("type") == "tool_use":
                                    tool_uses.append({
                                        "id": block.get("id"),
                                        "name": block.get("name"),
                                        "input": {}
                                    })
                                    # 도구 사용 알림
                                    tool_name = block.get("name")
                                    tool_list.append(tool_name)
                                    logging.info(f"session_key: {self.data.session_key} | [tool_list] {tool_name} is appended. Current tool list is {tool_list}")

                            # Tool use input 수집
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "input_json_delta" and tool_uses:
                                    # 마지막 tool_use의 input에 추가
                                    partial_json = delta.get("partial_json", "")
                                    if partial_json:
                                        # input을 점진적으로 누적. (==partial json. anthropic sdk처럼 snapshot을 안떠줌. 직접 모아서 표출해야함)
                                        current_input = tool_uses[-1].get("input", {})
                                        if isinstance(current_input, str):
                                            tool_uses[-1]["input"] = current_input + partial_json
                                        else:
                                            tool_uses[-1]["input"] = partial_json

                            # message_delta로 stop_reason 확인. 툴이 끝났을 때, 툴의 이름과 어떤 명령어를 mcp에서 쳤는지 파악 후 response로 전달
                            if data.get("type") == "message_delta":
                                stop_reason = data.get("delta", {}).get("stop_reason")
                                if stop_reason == "tool_use":
                                    response_dict["text"] = "\n\n\n"
                                    response_dict["tool_name"] = tool_uses[-1]["name"]
                                    response_dict["tool_text"] = tool_uses[-1]["input"]
                                if stop_reason == "end_turn":
                                    response_dict["is_end"] = True

                            # 정보가 있을 때만 답변 내려주기
                            if any([response_dict['text'], response_dict['model'], response_dict['tool_name'], response_dict['tool_text'], response_dict['is_end'], response_dict['thinking']]):
                                yield serialize_response(response_dict)
                                await asyncio.sleep(0)

                        # iter 후 동작. 툴이 추가된게 없으면 마지막 본문 메세지까지 전달 완료니 루프 종료
                        if not tool_uses:
                            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] No tool use detected. Finishing.")
                            break

                        # 툴이 추가된게 있으면 기존 내용 + 추가된 툴 정보까지 mcp에 전달해 명령을 수행하도록 해야함.
                        # text 블록을 assistant_content에 추가 (thinking 다음, tool_use 전에)
                        if current_text:
                            assistant_content.append({"type": "text", "text": current_text})

                        logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Executing {len(tool_uses)} tools")
                        tool_results = []

                        for tool_use in tool_uses:
                            prefixed_tool_name = tool_use.get("name")  # LLM이 선택한 prefix된 이름
                            tool_input = tool_use.get("input")
                            tool_id = tool_use.get("id")

                            if isinstance(tool_input, str):
                                try:
                                    tool_input = json.loads(tool_input)
                                except json.JSONDecodeError as e:
                                    logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Failed to parse tool input: {e}")
                                    tool_input = {}

                            # 해당 도구를 제공하는 MCP 클라이언트 찾기
                            target_mcp_client = tool_to_client_map.get(prefixed_tool_name)
                            if not target_mcp_client:
                                logging.error(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] No client found for tool: {prefixed_tool_name}")
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": f"Error: Tool {prefixed_tool_name} not found",
                                    "is_error": True
                                })
                                continue

                            # prefix 제거하여 원래 도구명 추출
                            # "mcp0__get_weather" -> "get_weather"
                            if "__" in prefixed_tool_name:
                                original_tool_name = prefixed_tool_name.split("__", 1)[1]
                            else:
                                # 혹시 prefix가 없는 경우 (하위 호환성)
                                original_tool_name = prefixed_tool_name

                            # MCP 서버에서 도구 실행 (원래 이름으로)
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
                                logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] Tool execution error: {e}")
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

                        # for next iter
                        messages.append({
                            "role": "assistant",
                            "content": assistant_content
                        })
                        # assistant_content shape =
                        messages.append({
                            "role": "user",
                            "content": tool_results
                        })

                        # body 업데이트
                        body_dict["messages"] = messages
                        body = json.dumps(body_dict) # 직렬화

                        iteration += 1

        except asyncio.TimeoutError:
            logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] TIMEOUT ERROR: {TIMEOUT}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.stream_with_mcp] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                yield make_error_response()
        finally:
            # 모든 MCP 클라이언트 연결 종료
            for client in mcp_clients:
                try:
                    await client.disconnect()
                    logging.info(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] MCP client disconnected")
                except Exception as e:
                    logging.error(f"session_key: {self.data.session_key} | [client.bedrock.stream_with_mcp] Error disconnecting MCP client: {e}")


    async def chat(self, is_retry: bool = False):
        try:
            modelId = self.get_model(is_retry=is_retry)
            body = await self.get_body()

            logging.info(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.chat] service: {self.data.service} | model: {modelId} | is_retry: {is_retry} | REQUEST to BEDROCK")
            async with self.get_async_client() as client:
                response = await client.invoke_model(
                    modelId=modelId,
                    body=body,
                    contentType='application/json'
                )
                response_dict = make_response(iteration=0)
                async for event in response["body"]:
                    data = json.loads(event.decode('utf-8'))
                    response_dict["text"] = data["content"][0]["text"]
                    response_dict["model"] = data["model"]
                response_dict["vendor"] = BEDROCK
                response_dict["is_end"] = True
            return response_dict

        except Exception as e:
            logging.error(f"session_key: {self.data.session_key} | [client.bedrock.BedrockClient.chat] ERROR: {e}")
            if not is_retry:
                raise FirstTryError()
            else:
                return make_error_response()


@dataclass
class S3Client(Boto3Session):
    access_key: str = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    region: str = os.getenv("AWS_DEFAULT_REGION")


    def get_async_client(self):
        """context manager 반환"""
        session = self.get_async_session()
        return session.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

    async def download_file_to_path(self, bucket:str, key:str, path:Path):
        try:
            async with self.get_async_client() as s3:
                with path.open("wb") as f:
                    await s3.download_fileobj(bucket, key, f)
        except Exception as e:
            logging.error(f"🔴 [client.bedrock.S3Client.download_file] Failed to download file from S3: {e}")
            raise Exception(e)
