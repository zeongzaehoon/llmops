import ast
from datetime import timedelta, datetime, timezone
from uuid import uuid4
from bson import ObjectId

from module.mcp.dto import *
from utils.error import *


def make_mcpArgs(args:dict) -> MCPArgs:
    """
    make llmArgs in order to seperated Action \n\n
    - redis_save:bool -> save conversation_history Y/n
    """
    try:
        return MCPArgs(
            # server stage
            server_stage=args.get('server_stage'),

            # session data
            session_key=args.get('session_key'),
            service=args.get('service', DEFAULT),
            agent=args.get('agent'),

            # llm-proxy
            vendor=args.get('vendor'),
            model=args.get('model'),
            question=args.get('question'),

            # client
            llm_proxy_client=args.get('llm_proxy_client'),
            main_db_client=args.get('main_db_client'),
            memory_db_client=args.get('memory_db_client'),
            s3_client=args.get('s3_client'),
            message_client=args.get('message_client'),

            # other
            info=args.get('info'),
            chat_info={**args.get('info'), **{"is_mcp": True, "agent": args.get('agent')}},
            lang=args.get('lang'),
            is_mcp=args.get('is_mcp'),
            start_time=args.get('start_time'),
            toolset_id=args.get('toolset_id'),
            segment_data=args.get('segment_data')
        )
    except DataError as e:
        logging.error(f"[module.mcp.helper.make_mcpArgs] 🔴 DataError: {e.message}")
        raise DataError(e.message)
    except Exception as e:
        logging.error(f"[module.mcp.helper.make_mcpArgs] 🔴 Exception: {e}")
        raise e


async def get_system_prompt(mcpArgs:MCPArgs):
    """
    get prompt from db.epic.prompt_history
    """
    try:
        prompt_result = await get_prompt_from_mongo(mcpArgs.main_db_client, **{'agent': mcpArgs.agent})
        if prompt_result:
            prompt = prompt_result[1]
            pid = str(prompt_result[0])
        else:
            prompt = "You are a helpful assistant"
            pid = None

        return prompt, pid
    except DBError as e:
        logging.error(f"[module.mcp.helper.get_system_prompt] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.mcp.helper.get_system_prompt] 🔴 Exception: {e}")
        raise e


async def get_prompt_from_mongo(main_db_client:MongoClient, **kwargs:dict):
    try:
        _filter = kwargs
        sort = [("date", -1)]
        result = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter=_filter, sort=sort)
        return result["_id"], result["prompt"]

    except DBError as e:
        logging.info(f"[module.mcp.helper.get_prompt_from_mongo] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.info(f"[module.mcp.helper.get_prompt_from_mongo] 🔴 Exception: {e}")
        raise e


async def get_conversation_history(mcpArgs:MCPArgs):
    """get conversation history from Redis"""
    try:
        count = await mcpArgs.memory_db_client.llen(mcpArgs.session_key)
        if count == 0:
            conversations = []
        else:
            conversations = await mcpArgs.memory_db_client.lrange(mcpArgs.session_key, -40, -1)

        result = decode_data_from_redis(conversations)
        return result

    except DBError as e:
        logging.error(f"[module.mcp.helper.get_conversation_history] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"[module.mcp.helper.get_conversation_history] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"[module.mcp.helper.get_conversation_history] 🔴 Exception: {e}")
        raise e


async def get_vendor_and_model(mcpArgs:MCPArgs):
    try:
        document = await mcpArgs.main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={'agent': mcpArgs.agent}
        )
        return document["vendor"], document["model"]

    except DBError as e:
        logging.error(f"[module.mcp.helper.get_vendor_and_model] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.mcp.helper.get_vendor_and_model] 🔴 Exception: {e}")
        raise e


async def get_mcp_toolset(mcpArgs:MCPArgs):
    try:
        if mcpArgs.toolset_id:
            agent_document = await mcpArgs.main_db_client.find_one(
                collection=AGENT_COLLECTION,
                filter={"_id": ObjectId(mcpArgs.toolset_id)}
            )
        else:
            agent_document = await mcpArgs.main_db_client.find_one(
                collection=AGENT_COLLECTION,
                filter={"agent": mcpArgs.agent, "isService": True}
            )

        mcp_info = agent_document["mcpInfo"]

        server_ids = list()
        tools_infos = dict()
        for mcp_info_each in mcp_info:
            server_ids.append(ObjectId(mcp_info_each["serverId"]))
            tools_infos[mcp_info_each["serverId"]] = mcp_info_each["tools"]

        server_documents = await mcpArgs.main_db_client.find(
            collection=MCP_SERVER_COLLECTION,
            filter={'_id': {'$in': server_ids}}
        )

        server_infos = {
            str(server_info["_id"]): {"name": server_info["name"], "uri": server_info["uri"], "token": server_info["token"]}
            for server_info in server_documents
        }

        result = list()
        for server_info_id in server_infos:
            final_object = server_infos[server_info_id]
            if server_info_id in tools_infos:
                final_object["tools"] = tools_infos[server_info_id]
                result.append(final_object)
        return result

    except DBError as e:
        logging.error(f"[module.mcp.helper.get_mcp_agent_info] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.mcp.helper.get_mcp_agent_info] 🔴 Exception: {e}")
        raise e


def decode_data_from_redis(list_data):
    """
    decode string data from redis -> dict
    """
    try:
        if len(list_data) == 0:
            result = []
        else:
            result = list(map(lambda string_data: ast.literal_eval(string_data), list_data))
        return result

    except Exception as e:
        logging.error(f"[module.mcp.helper.decode_data_from_redis] 🔴 Exception: {e}")
        raise e


def mcp_conv_hist_format(list_data):
    try:
        if not list_data:
            return []

        result = list()
        for data in list_data:
            role = data.get("role")
            message = data.get("message")

            if role == "human":
                # human 메시지는 그대로 추가
                result.append({"role": "human", "message": message})

            elif role == "ai":
                # ai 메시지는 iteration 리스트 형태
                try:
                    iterations = ast.literal_eval(message) if isinstance(message, str) else message
                except (ValueError, SyntaxError):
                    # 파싱 실패 시 텍스트로 처리
                    result.append({"role": "ai", "message": message})
                    continue

                if not isinstance(iterations, list):
                    result.append({"role": "ai", "message": str(iterations)})
                    continue

                # 각 iteration 처리
                for iteration in iterations:
                    # assistant_content가 있으면 추가 (tool_use 포함)
                    if iteration.get("assistant_content"):
                        result.append({"role": "ai", "message": iteration["assistant_content"]})

                    # tool_results가 있으면 user role로 추가
                    if iteration.get("tool_results"):
                        result.append({"role": "human", "message": iteration["tool_results"]})

                # 마지막 iteration의 최종 텍스트 응답
                last_iter = iterations[-1] if iterations else {}
                if last_iter.get("is_end") and last_iter.get("text"):
                    result.append({"role": "ai", "message": last_iter["text"]})

        return result

    except Exception as e:
        logging.error(f"[module.mcp.helper.mcp_conv_hist_format] Exception: {e}")
        raise e


def redis_format(role, message, id=None, mcp_tools=None):
    """Redis input data format"""
    try:
        form = {
            "message": message,
            "role": role
        }
        if mcp_tools and role == "human":
            form["mcp_tools"] = mcp_tools
            form["id"] = id
        if id != None and role == "ai":
            form["id"] = id
            form["rating"] = None
        return str(form)
    except Exception as e:
        logging.error(f"[module.mcp.helper.redis_format] 🔴 Exception: {e}")
        raise e


async def save_to_memory_db(
    memory_db_client:RedisClient,
    session_key:str,
    message:str,
    role:str
):
    try:
        data_redis = redis_format(role=role, message=message)
        await memory_db_client.rpush(session_key, data_redis)
        await memory_db_client.set_expire(session_key, REDIS_EXPIRE_TIME)
    except MemoryDBError as e:
        logging.info(f"[module.mcp.helper.save_to_memory_db] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.info(f"[module.mcp.helper.save_to_memory_db] 🔴 Exception: {e}")
        raise e


def make_chat_history_data(
    chat_info:dict,
    role:str,
    message:str,
    token:int,
    reg_date:datetime=None,
    session_key:str = None,
    agent: str = None,
    url: str = None,
):
    try:
        chat_info['sessionKey'] = session_key
        chat_info['agent'] = agent
        chat_info['date'] = reg_date or datetime.now(timezone.utc)
        chat_info['role'] = role
        chat_info['message'] = message
        chat_info['token'] = token
        chat_info['is_mcp'] = True
        chat_info["mcp_tools"] = str(chat_info["mcp_tools"]) if chat_info.get("mcp_tools") else None
        chat_info["model"] = chat_info.get("model")
        chat_info["rating"] = 0
        if agent == SCHEMASIMPLE:
            chat_info['url'] = url

        return chat_info
    except Exception as e:
        logging.error(f"[module.mcp.helper.make_chat_history_data] 🔴 Exception: {e}")
        raise e

def mongo_format(session_key, role, message, extra:dict=None, service_type:str=None):
    """몽고 DB input data format"""
    form = {
        "sessionKey": session_key,
        "role": role,
        "message": message,
        "date": datetime.now(timezone.utc),
        "rating":0
    }
    if extra:
        form = {**form, **extra}
    if service_type:
        form['serviceType'] = service_type
    return form


def make_human_message(question, retrieval_data=None, language_message=None, segment_data=None):
    result = f"<{USER_QUESTION_NAME}>\n{question}\n</{USER_QUESTION_NAME}>"
    if segment_data:
        result = f"<{SEGMENT_DATA_NAME}>\n{segment_data}\n</{SEGMENT_DATA_NAME}>\n\n\n{result}"
    if retrieval_data:
        result = f"<{RAG_NAME}>\n{retrieval_data}\n</{RAG_NAME}>\n\n\n{result}"
    if language_message:
        result = result + f"\n\n\n<{LANG_NAME}>\n{language_message}\n</{LANG_NAME}>"
    return result


async def make_error_message_for_LLM(streaming:bool=True):
    try:
        message = "죄송합니다. 에러가 발생해 답변을 제공할 수 없습니다. 계속 같은 메세지를 받으신다면 담당자에게 연락주시면 감사하겠습니다."
        if streaming:
            for m in message:
                await asyncio.sleep(0.025)
                yield m
        else:
            yield message

    except Exception as e:
        logging.error(f"[module.mcp.helper.make_error_message] 🔴 Exception: {e}")
        raise e


def get_elapsed(mcpArgs:MCPArgs, key:str):
    try:
        end_time = time.time()
        elapsed = timedelta(seconds=float(end_time - mcpArgs.start_time)).total_seconds()
        mcpArgs.time_info[key] = elapsed
    except Exception as e:
        logging.error(f"[module.mcp.helper.get_elapsed] 🔴 Exception: {e}")
        raise e


def write_log_for_debug_message(system_message=None, conversation_history=None, human_message=None):
    logging.info("*"*100)
    logging.info(f"[시스템 프롬프트] {system_message}")
    logging.info("*"*100)
    logging.info(f"[대화 이력] {conversation_history}")
    logging.info("*"*100)
    logging.info(f"[사용자 프롬프트] {human_message}")
    logging.info("*"*100)


def make_error_message(agent, lang: str = None):
    lang = lang or LANG_KO
    message = LANG_EN_ERR_MESSAGE if lang == LANG_EN else LANG_JA_ERR_MESSAGE if lang == LANG_JA else LANG_KO_ERR_MESSAGE

    response = {
        "iteration": None,
        "text": None,
        "model": None,
        "vendor": None,
        "tool_name": "🔴 Error",
        "tool_text": message,
        "thinking": None,
        "is_error": True,
        "is_end": True
    } if agent in MESSAGE_STRUCTURE_LIST else message

    return response


async def record_err_to_main_db(args: dict):
    base_document = {
        "sessionKey": args.get("session_key"),
        "agent": args.get('agent'),
        "vendor": args.get('vendor'),
        "model": args.get('model'),
        "isError": True,
    }
    if args.get("lang"):
        base_document["language"] = args["lang"]
    if args.get("info_eagle"):
        base_document = {**base_document, **args["info_eagle"]}
    if args.get("info_user"):
        base_document = {**base_document, **args["info_user"]}

    error_message = LANG_EN_ERR_MESSAGE if args.get("lang") == LANG_EN else LANG_JA_ERR_MESSAGE if args.get("lang") == LANG_JA else LANG_KO_ERR_MESSAGE

    question_document = {**base_document, **{"message": args.get('question'), "role": ROLE_HUMAN, 'date': datetime.now(timezone.utc)}}
    answer_document = {**base_document, **{"message": error_message, "role": ROLE_AI, 'date': datetime.now(timezone.utc)}}
    documents = [question_document, answer_document]

    main_db_client: MongoClient = args.get("main_db_client")
    await main_db_client.insert_many(CHAT_COLLECTION, documents)
