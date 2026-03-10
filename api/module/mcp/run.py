import orjson

from module.mcp.helper import *
from utils.error import *
from utils.vector import get_token_length



async def run_mcp(mcpArgs:MCPArgs):
    try:
        # multi Language: question is set on api layer, side
        mcpArgs.language_message = LANG_JA_MESSAGE if mcpArgs.lang == LANG_JA else LANG_EN_MESSAGE if mcpArgs.lang == LANG_EN else LANG_KO_MESSAGE

        # calculate token size
        human_message = make_human_message(question=mcpArgs.question, language_message=mcpArgs.language_message, segment_data=mcpArgs.segment_data) # for sent & for cal token
        str_for_token_length = mcpArgs.system_message + str(mcpArgs.conversation_history) + human_message
        mcpArgs.chat_info['token'] = get_token_length(str_for_token_length, mcpArgs.model)

        # save question to Database
        data_mongo = mongo_format(mcpArgs.session_key, "human", mcpArgs.question, mcpArgs.chat_info)
        result = await mcpArgs.main_db_client.insert_one(collection="solomonChatHistory", document=data_mongo)
        mcpArgs.chat_info["cid"] = str(result.inserted_id) # save cid for tie question-answer

        # time test
        end_time = time.time()
        elapsed = timedelta(seconds=float(end_time - mcpArgs.start_time))
        logging.info(f"session_key: {mcpArgs.session_key} | [TIMETEST] ⏱️ TIME to proxy: {elapsed}")

        # log for debug message
        # write_log_for_debug_message(
        #     system_message=mcpArgs.system_message,
        #     conversation_history=mcpArgs.conversation_history,
        #     human_message=human_message
        # )

        is_first_chunk = True
        async for mcpArgs.response in mcpArgs.llm_proxy_client.stream_with_mcp(
            mcp_info=mcpArgs.mcp_info,
            service=mcpArgs.service,
            vendor=mcpArgs.vendor,
            model=mcpArgs.model,
            system_message=mcpArgs.system_message,
            human_message=human_message,
            conversation_history=mcpArgs.conversation_history,
            time=float(mcpArgs.start_time),
            session_key=mcpArgs.session_key
        ):
            if mcpArgs.response and isinstance(mcpArgs.response, GroxyStreamingResponse): # mcp일 경우엔 dict를 str로 serialize해서 보냄. client에서 json.loads로 dict 변환 중.
                if is_first_chunk:
                    # 첫번째 답변 떨어졌을 때 시간 체크 및 기타 상태값 변경
                    is_first_chunk = False

                    # 시간 체크
                    if mcpArgs.start_time:
                        time_from_proxy = time.time()
                        elapsed = timedelta(seconds=float(time_from_proxy - mcpArgs.start_time))
                        logging.info(f"session_key: {mcpArgs.session_key} | [TIMETEST] ⏱️ TIME from proxy: {elapsed}")

                # 정상응답
                if mcpArgs.agent in MESSAGE_STRUCTURE_LIST:
                    response = {
                        "iteration": mcpArgs.response.iteration,
                        "text": mcpArgs.response.text,
                        "model": mcpArgs.response.model,
                        "vendor": mcpArgs.response.vendor,
                        "tool_name": mcpArgs.response.tool_name,
                        "tool_text": mcpArgs.response.tool_text,
                        "thinking": mcpArgs.response.thinking,
                        "is_error": mcpArgs.response.is_error,
                        "is_end": mcpArgs.response.is_end
                    }
                    if response["is_error"]:
                        response = make_error_message(mcpArgs.agent, mcpArgs.lang)
                    yield orjson.dumps(response)

                else: # on service: schemaSimple
                    # 텍스트
                    text = getattr(mcpArgs.response, "text", None)
                    if text:
                        yield text

                    # 에러 체크
                    is_error = getattr(mcpArgs.response, "is_error", None)
                    if is_error:
                        error_text = LANG_JA_ERR_MESSAGE if mcpArgs.lang == LANG_JA else LANG_EN_ERR_MESSAGE if mcpArgs.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                        for word in error_text:
                            yield word
                        err_message = "LLM-PROXY send Error. first try and retry are failed."
                        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 LLMStreamingError: {err_message}")

                mcpArgs.full_response.append(mcpArgs.response)

        await callback(mcpArgs)

    except DBError as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except VectorDBError as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except AWSError as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except LLMStreamingError as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 LLMStreamingError: {e.message}")
        raise LLMStreamingError(e.message)
    except Exception as e:
        logging.error(f"session_key: {mcpArgs.session_key} | [module.mcp.run.run_mcp] 🔴 Exception: {e}")
        raise e


def _create_data_iter() -> dict:
    """iteration 별 데이터 구조 초기화"""
    return {
        'text': str(),
        'tool_name': None,
        'tool_text': None,
        'thinking': str(),
        'assistant_content': list(),
        'tool_results': list(),
        'is_end': False,
        'is_error': False
    }


def _parse_json_field(value) -> list:
    """str/bytes 타입이면 JSON 파싱, 아니면 그대로 반환"""
    return orjson.loads(value) if isinstance(value, (str, bytes)) else value


async def callback(args: MCPArgs):
    try:
        # 시간 기록
        end_time = time.time()
        elapsed = timedelta(seconds=float(end_time - args.start_time))
        logging.info(f"session_key: {args.session_key} | [TIMETEST] ⏱️ TIME to callback: {elapsed}")
        reg_date = datetime.now(timezone.utc)

        # 스트리밍 데이터 파싱
        current_iteration = 0
        data_iter = _create_data_iter()
        redis_data = []
        mcp_tools = []
        is_error = False
        error_text = ""
        for response in args.full_response:
            # 모델, 벤더 기록
            if getattr(response, "model", None):
                args.chat_info["model"] = response.model
            if getattr(response, "vendor", None):
                args.chat_info["vendor"] = response.vendor

            # iteration 변경 시 기존 데이터 저장 및 초기화
            if current_iteration != response.iteration:
                redis_data.append(data_iter)
                data_iter = _create_data_iter()
                current_iteration = response.iteration

            # 스트리밍 데이터 누적
            text = getattr(response, "text", None)
            thinking = getattr(response, "thinking", None)
            tool_name = getattr(response, "tool_name", None)
            tool_text = getattr(response, "tool_text", None)
            assistant_content = getattr(response, "assistant_content", None)
            tool_results = getattr(response, "tool_results", None)
            is_end = getattr(response, "is_end", False)
            is_error = getattr(response, "is_error", False)

            if text:
                data_iter['text'] += text
            if thinking:
                data_iter['thinking'] += thinking
            if tool_name:
                data_iter['tool_name'] = tool_name
            if tool_text:
                data_iter['tool_text'] = tool_text
            if tool_name and tool_text:
                mcp_tools.append({tool_name: tool_text})
            if assistant_content:
                data_iter['assistant_content'] = _parse_json_field(assistant_content)
            if tool_results:
                data_iter['tool_results'] = _parse_json_field(tool_results)
            if is_error:
                args.chat_info["llmProxyError"] = True
                error_text = LANG_JA_ERR_MESSAGE if args.lang == LANG_JA else LANG_EN_ERR_MESSAGE if args.lang == LANG_EN else LANG_KO_ERR_MESSAGE
                data_iter['is_error'] = True
                data_iter['text'] += f"\n\n{error_text}"
            if is_end:
                data_iter['is_end'] = True
                redis_data.append(data_iter)

        if args.message_client and is_error:
            message = f"🔴 session_key: {args.session_key}, agent: {args.agent} | [solomon-api] LLM-PROXY send Error. Both initial attempt and retry failed."
            await args.message_client.send_message(channel='casual', message=message)
        args.message = redis_data[-1].get("text") if not is_error else error_text
        args.chat_info["mcp_tools"] = mcp_tools

        # 비동기 작업 실행
        question_data_redis = redis_format(role="human", message=args.question)
        answer_data_redis = redis_format(role="ai", message=str(redis_data))
        data_mongo = make_chat_history_data(
            args.chat_info,
            role="ai",
            message=args.message,
            token=get_token_length(args.message),
            reg_date=reg_date,
            session_key=args.session_key,
            agent=args.agent,
            url=args.question
        )

        await asyncio.gather(
            args.memory_db_client.rpush(args.session_key, question_data_redis),
            args.memory_db_client.rpush(args.session_key, answer_data_redis),
            args.memory_db_client.set_expire(args.session_key, 1800),
            args.main_db_client.insert_one(collection="solomonChatHistory", document=data_mongo)
        )

    except DBError as e:
        logging.error(f"session_key: {args.session_key} | [module.mcp.run.callback] 🔴 DBError: {e.message}")
    except MemoryDBError as e:
        logging.error(f"session_key: {args.session_key} | [module.mcp.run.callback] 🔴 MemoryDBError: {e.message}")
    except AWSError as e:
        logging.error(f"session_key: {args.session_key} | [module.mcp.run.callback] 🔴 AWSError: {e.message}")
    except Exception as e:
        logging.error(f"session_key: {args.session_key} | [module.mcp.run.callback] 🔴 Exception: {e}")
