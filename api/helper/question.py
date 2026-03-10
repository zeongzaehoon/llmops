import ast
import re
import json
import orjson
import pytz
import codecs
import html2text
from uuid import uuid4
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from pydantic import HttpUrl, ValidationError
from fastapi.responses import StreamingResponse

from client.mongo import MongoClient
from client.redis import RedisClient
from client.aws import S3Client
from payload.question import askPayload, AskDashboardPayload, insertInitReportchatRowPayload, getReportChatDatasPayload
from utils.error import *
from module.llm.activate import RunLLM as RunLLMProxy
from module.mcp.activate import RunMCP as RunMCPProxy



def get_vector_db_index(category:str, server_stage:str) -> str:
    if category in UXGPT_LIST or category == VOC:
        vector_db_index = CONTACTUS_INDEX if server_stage == PRODUCTION else CONTACTUS_STAGING_INDEX
    elif category == REPORTCHAT:
        vector_db_index = REPORTCHAT_INDEX
    else:
        vector_db_index = MAIN_INDEX
    return vector_db_index


async def streaming_response(
        response: ResponseQueue,
        generator, ask_id:str=None,
        is_error:bool=None,
        start_time=None,
        session_key:str=None
):
    try:
        if not is_error:
            asyncio.create_task(make_response_with_queue(
                response=response,
                generator=generator
            ))
        else:
            asyncio.create_task(make_err_response_with_queue(
                response=response,
                generator=generator
            ))
        await response.event.wait()
        if start_time:
            time_first_chunk_in_queue = time.time()
            elapsed = timedelta(seconds=int(time_first_chunk_in_queue - start_time))
            logging.info(f"session_key: {session_key} | [TIMETEST] ⏱️ TIME from queue: {elapsed}")
        return StreamingResponse(
            stream_from_queue(response),
            headers={
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache",
                "Transfer-Encoding": "chunked",
                "Id": ask_id if ask_id else "",
                "askCode": "200" if not is_error else "599",
                "Request-Id": response.request_id
            },
            media_type="text/event-stream",
            status_code=200
        )

    except DBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 DBError: {e}")
        raise LLMStreamingError
    except LLMStreamingError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 LLMStreamingError: {e}")
        raise LLMStreamingError
    except MemoryDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 MemoryDBError: {e}")
        raise LLMStreamingError
    except VectorDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 VectorDBError: {e}")
        raise LLMStreamingError
    except AWSError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 AWSError: {e}")
        raise LLMStreamingError
    except Exception as e:
        logging.info(f"[helper.question.streaming_response] 🔴 error: {e}")
        raise LLMStreamingError


async def make_response_with_queue(response: ResponseQueue, generator):
    try:
        # 대답이 들어오면 대답을 비동기 큐에 넣어준다.
        async for chunk in generator:
            await response.queue.put((response.request_id, chunk))
            if not response.event.is_set():
                response.event.set()
    except DBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 DBError: {e}")
        raise LLMStreamingError
    except LLMStreamingError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 LLMStreamingError: {e}")
        raise LLMStreamingError
    except MemoryDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 MemoryDBError: {e}")
        raise LLMStreamingError
    except VectorDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 VectorDBError: {e}")
        raise LLMStreamingError
    except AWSError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 AWSError: {e}")
        raise LLMStreamingError
    except Exception as e:
        logging.info(f"[helper.question.streaming_response] 🔴 error: {e}")
        raise LLMStreamingError
    finally:
        await response.queue.put((response.request_id, None))


async def make_err_response_with_queue(response: ResponseQueue, generator):
    try:
        # 대답이 들어오면 대답을 비동기 큐에 넣어준다.
        async for chunk in generator:
            await response.queue.put((response.request_id, chunk))
            if not response.event.is_set():
                response.event.set()
    except DBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 DBError: {e}")
        raise LLMStreamingError
    except LLMStreamingError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 LLMStreamingError: {e}")
        raise LLMStreamingError
    except MemoryDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 MemoryDBError: {e}")
        raise LLMStreamingError
    except VectorDBError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 VectorDBError: {e}")
        raise LLMStreamingError
    except AWSError as e:
        logging.info(f"[helper.question.streaming_response] 🔴 AWSError: {e}")
        raise LLMStreamingError
    except Exception as e:
        logging.info(f"[helper.question.streaming_response] 🔴 error: {e}")
        raise LLMStreamingError
    finally:
        await response.queue.put((response.request_id, None))



async def stream_from_queue(response: ResponseQueue):
    while True:
        request_id, chunk = await response.queue.get()

        if request_id != response.request_id:
            continue

        if chunk is None:
            response.queue.task_done()
            break

        yield chunk


async def get_s3_content(s3_client:S3Client, s3_path:str):
    try:
        bucket, key = s3_path.split(':')
        download_file = await s3_client.download_file(bucket=bucket, key=key)
        result = download_file.decode('utf-8')
        return result

    except AWSError as e:
        logging.info(f"[helper.question.get_s3_content] 🔴 AWSError: {e}")
        raise e
    except Exception as e:
        logging.info(f"[helper.question.get_s3_content] 🔴 error: {e}")
        raise e


def make_args_for_contactus(session_key:str, payload:askPayload, server_stage: str):
    try:
        service = CS_PRODUCTION if server_stage == PRODUCTION else CS_STAGING
        if payload.agent not in UXGPT_LIST:
            return {"error": {"agent": True}}

        result = {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question,
            "lang": payload.lang,
            "session_key": session_key,
            "info_eagle": payload.info if payload.agent == CONTACTUS else None,
            "ask_id": str(uuid4())
        }
        # GEO contactUs는 payload에 lang을 안담음. info에 있으면 꺼내서 담아주기
        if result["lang"] is None and payload.info and isinstance(payload.info, dict) and payload.info.get('lang'):
            result['lang'] = payload.info['lang']
        # contactUs에 adminStatus init을 안넣어주는 iFrame이 있음. contactUs일 땐, 강제로 주입
        if payload.agent == CONTACTUS and isinstance(result.get('info_eagle'), dict) and result.get('info_eagle'):
            result['info_eagle']["adminStatus"] = "init"

        return result
    except Exception as e:
        logging.info(f"[helper.question.make_args_for_contactus] 🔴 error: {e}")
        raise e


async def make_args_for_docent(memory_db_client: RedisClient, session_key:str, payload:askPayload | AskDashboardPayload, server_stage: str):
    try:
        if payload.agent not in SERVICE_LIST:
            logging.error(f"[helper.question.make_args_for_docent] category:{payload.agent} is not enrolled in SERVICE LIST")
            return {"error": {"agent": True}}

        info = payload.info
        if not info: # playground에서 입력된 경우, eagle에 데이터가 넘어가면 안됨. filter용으로 pg True 추가
            info = {"pg": True}
        lang = info.get("lang", LANG_KO) if info else LANG_KO

        category = payload.agent
        if category == REPORTCHAT:
            service = REPORTCHAT_PRODUCTION if server_stage == PRODUCTION else REPORTCHAT_STAGING
        elif category == DASHBOARDCHAT:
            service = DASHBOARDCHAT_PRODUCTION if server_stage == PRODUCTION else DASHBOARDCHAT_STAGING
        elif category == SCROLLCHAT:
            service = SCROLLCHAT_PRODUCTION if server_stage == PRODUCTION else SCROLLCHAT_STAGING
        elif category == SCHEMACHAT or category == WHITEPAPER or category == CXTRENDS:
            service = GEO_CHAT_PRODUCTION if server_stage == PRODUCTION else GEO_CHAT_STAGING
        else:
            service = DEFAULT

        question = payload.question
        if not question:
            question = "선택된 데이터를 기반으로 전체적인 분석내용을 말해줘." if lang == LANG_KO else "選択されたデータに基づいて、全体的な分析内容を教えてください。 \n\n 日本語で答えてください。" if lang == LANG_JA else "Please tell me the overall analysis content based on the selected data. \n\n Please respond in English." if lang == LANG_EN else None
            is_report_chat_init = True
        else:
            is_report_chat_init = False

        result = {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": category,
            "question": question,
            "session_key": session_key,
            "info_user": info,
            "is_report_chat_init": is_report_chat_init,
            "lang": lang,
            "ask_id": str(uuid4()),
            "is_demo": payload.is_demo
        }

        is_set_report = await memory_db_client.get(key=f"rc_id:{session_key}")
        if not is_set_report:
            result["error"] = {"isNotSetReportKR" if lang == LANG_KO else "isNotSetReportJA" if lang == LANG_JA else "isNotSetReportEN": True}
        else:
            if category == REPORTCHAT or category == DASHBOARDCHAT:
                result['baAIReportId'] = ast.literal_eval(is_set_report)
            elif category == SCROLLCHAT:
                result['beusAIReportId'] = ast.literal_eval(is_set_report)
            elif category == SCHEMACHAT or category == WHITEPAPER or category == CXTRENDS:
                result['geoAIReportId'] = ast.literal_eval(is_set_report)
            tasks = [
                memory_db_client.set_expire(key=f"rc:{session_key}", time=SET_REPORT_REDIS_EXPIRE_TIME),
                memory_db_client.set_expire(key=f"rc_id:{session_key}", time=SET_REPORT_REDIS_EXPIRE_TIME),
            ]
            await asyncio.gather(*tasks)

        return result

    except Exception as e:
        logging.info(f"[helper.question.make_args_for_reportchat] 🔴 error: {e}")
        raise e


def make_args_for_schematag(session_key:str, payload:askPayload, server_stage:str):
    try:
        service = GEO_JSON_PRODUCTION if server_stage == PRODUCTION else GEO_JSON_STAGING

        result = {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question,
            "session_key": session_key,
            "ask_id": str(uuid4()),
            "lang": payload.lang,
        }
        return result

    except Exception as e:
        logging.info(f"[helper.question.make_args_for_schematag] 🔴 error: {e}")
        raise e


async def insert_chat_history(main_db_client:MongoClient, args:dict):
    try:
        tasks = list()

        init_row = {
            "sessionKey": args["session_key"],
            "role": "human",
            "message": args["question"],
            "date": datetime.now(timezone.utc),
            "rating": 0,
            "agent": args["agent"],
            "model": args["model"],
            "ask_id": args["ask_id"],
            "is_demo": args["is_demo"],
            **args["info_user"]
        }
        if 'baAIReportId' in args:
            init_row['baAIReportId'] = args['baAIReportId']
        elif 'beusAIReportId' in args:
            init_row['beusAIReportId'] = args['beusAIReportId']
        elif 'geoAIReportId' in args:
            init_row['geoAIReportId'] = args['geoAIReportId']

        tasks.append(main_db_client.insert_one(collection="solomonChatHistory", document=init_row))
        if args.get("error") and any([args["error"].get("isNotSetReportKR"), args["error"].get("isNotSetReportJA"), args["error"].get("isNotSetReportEN")]):
            error_row = {
                **init_row,
                "role": "ai",
                "message": ERR_REPORT_CHAT_KR if args["lang"] == LANG_KO else ERR_REPORT_CHAT_JA if args["lang"] == LANG_JA else ERR_REPORT_CHAT_EN,
            }
            error_row.pop("model", None)
            tasks.append(main_db_client.insert_one(collection="solomonChatHistory", document=error_row))

        result = await asyncio.gather(*tasks)
        return result[0].inserted_id

    except DBError as e:
        logging.info(f"[helper.question.insert_chat_history] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.insert_chat_history] 🔴 error: {e}")
        raise e


def make_args_for_heatmap(session_key:str, payload:askPayload, server_stage: str):
    try:
        service = UXHEATMAP_AIREPORT_PRODUCTION if server_stage == PRODUCTION else UXHEATMAP_AIREPORT_STAGING

        return {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question,
            "session_key": session_key,
            "ask_id": str(uuid4()),
            "lang": payload.lang,
            "images": [get_public_url("beusable-ai-report:heatmap/20260108/6940e2eb6af1f0741d73176b/695effb051896e2d2bd672e6/capture-scroll.png")]
        }
    except Exception as e:
        logging.info(f"[helper.question.make_args_for_abtest] 🔴 error: {e}")
        raise e


async def make_args_for_voc(main_db_client:MongoClient, session_key:str, payload:askPayload, server_stage: str):
    try:
        inbox = await main_db_client.find_one(collection="AIEmail", filter={"_id": ObjectId(payload.id)})
        fields = ['fromMail', 'fromName', 'company', 'toMail', 'toName', 'processedAt', 'subject', 'lastContent', 'status']
        received_email = {field: inbox.get(field) for field in fields}
        keyword_for_vector = inbox.get('keyword')

        references_list = []
        if inbox.get('references'):
            references_query = {'messageId': {'$in': inbox['references']}}
            projection = {field: 1 for field in fields}
            references_data = await main_db_client.find(collection="AIEmail", filter=references_query, projection=projection)
            if references_data:
                for ref in references_data:
                    references_list.append(make_json_serializable(ref))
        service = VOC_PRODUCTION if server_stage == PRODUCTION else VOC_STAGING
        return {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question or "",
            "mail": make_json_serializable(received_email),
            "references": references_list,
            "session_key": session_key,
            "keyword_for_vector": keyword_for_vector,
            "redis_save": False
        }
    except DBError as e:
        logging.info(f"[helper.question.make_args_for_eagle_mail] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.make_args_for_eagle_mail] 🔴 error: {e}")
        raise e


def make_args_for_dashboard(session_key:str, payload:askPayload, server_stage:str):
    try:
        service_name_dict = {
            DASHBOARD: DASHBOARD_PRODUCTION if server_stage == PRODUCTION else DASHBOARD_STAGING,
            DASHBOARDHELL: DASHBOARDHELL_PRODUCTION if server_stage == PRODUCTION else DASHBOARDHELL_STAGING,
        }

        result = {
            "agent": payload.agent,
            "session_key": session_key,
            "service": service_name_dict.get(payload.agent, JOURNEYMAP_DASHBOARD),
            "model": payload.model,
            "vendor": payload.vendor,
            "question": payload.question,
            "dashboard_data": DASHBOARD_SAMPLE if not payload.agent == DASHBOARDGA else DASHBOARDGA_SAMPLE,
            "redis_save": False,
            "lang": payload.lang,
            "current_time": pytz.timezone('Asia/Seoul').localize(datetime.now()),
            "ask_id": str(uuid4()).replace("-", ""),
            "segment_doc": payload.segment_doc
        }
        return result

    except Exception as e:
        logging.info(f"[helper.question.make_args_for_abtest] 🔴 error: {e}")
        raise e


def make_args(session_key:str, payload:askPayload, server_stage: str):
    try:
        if payload.agent not in SERVICE_LIST:
            logging.error(f"[helper.question.make_args] category:{payload.agent} is not enrolled in SERVICE LIST")
            return {"error": {"agent": True}}

        result = {
            "service": DEFAULT,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question,
            "session_key": session_key,
            "ask_id": str(uuid4())
        }

        return result
    except Exception as e:
        logging.info(f"[helper.question.make_args] 🔴 error: {e}")
        raise e


async def helper_get_and_make_dash_data(is_test:bool=False):
    try:
        if is_test:
            return DASHBOARD_SAMPLE

        import httpx
        tasks = list()
        paths = ["", "", ""]
        dashboard_data = dict()
        for path in paths:
            tasks.append(httpx.post(path))

        responses_from_hub = await asyncio.gather(*tasks)

        for path, response in zip(paths, responses_from_hub):
            dashboard_data[path] = str(response)

        return dashboard_data

    except Exception as e:
        logging.error(f"[helper.question.helper_get_and_make_dash_data] Exception: {e}")
        raise e


async def helper_get_ai_dashboard_html_from_main_db(s3_client: S3Client, main_db_client:MongoClient, ask_id:str, session_key:str=None):
    try:
        # get from baAIReport
        try:
            _filter = {"_id": ObjectId(ask_id)}
            collection = "baAIReport"
            from_solomon = False
            logging.info(f"[helper.question.helper_get_ai_dashboard_html_from_main_db] REQUEST FROM MINE")
        except:
            _filter = {'category': 'dashboard', 'ask_id': ask_id, "role": "ai"}
            collection = CHAT_COLLECTION
            from_solomon = True
            logging.info(f"[helper.question.helper_get_ai_dashboard_html_from_main_db] REQUEST FROM SOLOMON")

        doc = await main_db_client.find_one(collection=collection, filter=_filter)
        if not from_solomon:
            if doc:
                s3_path = doc["reportS3Path"]
                bucket, key = s3_path.split(":")
                html_str = await s3_client.download_file(bucket, key)
                return html_to_markdown(html_str.decode("utf-8"))
            else:
                return None # for raising Error

        else:
            if doc:
                html_str = doc['message']
                return html_str
            else:
                return None # for raising Error
    except DBError as e:
        logging.error(f"[helper.question.helper_get_ai_dashboard_html_from_main_db] DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.error(f"[helper.question.helper_get_ai_dashboard_html_from_main_db] Exception: {e}")
        raise e


def remove_code_blocks(html_str):
    pattern = r'```[\w]*\n?(.*?)```'
    return re.sub(pattern, r'\1', html_str, flags=re.DOTALL).strip()


def remove_escape_in_html_str(html_str):
    has_escape = '\\n' in html_str or '\\"' in html_str or '\\t' in html_str
    if (html_str.startswith('<!DOCTYPE') or html_str.startswith('<html')) and not has_escape:
        return html_str
    else:
        return codecs.decode(html_str, 'unicode_escape')


async def get_prompt_from_mongo(main_db_client:MongoClient, category:str, kind:str='prompt', order:int=None):
    """
    role:
    get prompt which is saved in MongoDB

    args:
    category: pathname
    kind: prompt type
    order: indepth order
    """
    try:
        filter = {'category':category} if category else {'category':'main'}
        if kind:
            filter['kind'] = kind
        if order:
            filter['order'] = order
        sort = [('date', -1)]
        result = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter=filter, sort=sort)
        return [result['_id'], result['prompt']]

    except DBError as e:
        logging.info(f"[helper.question.get_prompt_from_mongo] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.get_prompt_from_mongo] 🔴 error: {e}")
        raise e


def make_mcp_args(session_key:str, payload:askPayload, server_stage:str):
    try:
        if payload.agent not in SERVICE_LIST:
            logging.error(f"[helper.question.make_args] agent:{payload.agent} is not enrolled in SERVICE LIST")
            return {"error": {"agent": True}}

        service = get_mcp_service(payload.agent, server_stage)
        result = {
            "service": service,
            "vendor": payload.vendor,
            "model": payload.model,
            "agent": payload.agent,
            "question": payload.question,
            "session_key": session_key,
            "ask_id": str(uuid4()),
            "is_mcp": payload.is_mcp,
            "toolset_id": payload.toolset_id,
            "info": payload.info or {"pg": True},
            "segment_data": payload.segment_data
        }
        if result.get('info') and result['info'].get('lang'):
            result['lang'] = result['info']['lang']

        return result

    except Exception as e:
        logging.info(f"[helper.question.make_args] 🔴 error: {e}")
        raise e


def get_mcp_service(agent:str, server_stage:str):
    # mcp agent: [JOURNEYMAPMCP, CXDATATRENDMCP, SCHEMAJSON, SCHEMASIMPLE]
    if agent == JOURNEYMAPMCP:
        service = JOURNEYMAPMCP_PRODUCTION if server_stage == PRODUCTION else JOURNEYMAPMCP_STAGING
    elif agent == CXDATATRENDMCP:
        service = CXDATATRENDMCP_PRODUCTION if server_stage == PRODUCTION else CXDATATRENDMCP_STAGING
    elif agent == SCHEMAJSON:
        service = GEO_JSON_PRODUCTION if server_stage == PRODUCTION else GEO_JSON_STAGING
    elif agent == SCHEMASIMPLE:
        service = GEO_SIMPLE_PRODUCTION if server_stage == PRODUCTION else GEO_SIMPLE_STAGING
    elif agent == BIMCP:
        service = BIMCP_PRODUCTION if server_stage == PRODUCTION else BIMCP_STAGING
    else:
        service = DEFAULT

    return service



async def check_url_valid(args:dict):
    agent = args.get("agent")

    if agent == SCHEMASIMPLE:
        question = args.get("question")
        lang = args.get("lang")
        session_key = args.get("session_key")
        info = args.get("info")
        main_db_client: MongoClient = args.get("main_db_client")
        try:
            HttpUrl(question)
            return None
        except ValidationError as e:
            logging.error(f"[helper.question.make_mcp_args] {e}")
            error_key_map = {
                LANG_KO: "notSchemaURL",
                LANG_JA: "notSchemaURLJA",
                LANG_EN: "notSchemaURLEN",
            }
            question_lang = detect_mixed_language(question)
            error_key = error_key_map[question_lang] if question_lang in error_key_map else error_key_map.get(lang, "notSchemaURLEN")
            error_message = NOT_SCHEMA_URL_KR if error_key=="notSchemaURL" else NOT_SCHEMA_URL_EN if error_key=="notSchemaURLEN" else NOT_SCHEMA_URL_JP

            default_doc = {**{"sessionKey": session_key, "agent": agent, "date": datetime.now(timezone.utc), "rating": 0}, **info}
            question_doc = {**default_doc, **{"role": "human", "message": question}}
            answer_doc = {**default_doc, **{ "role": "ai", "message": error_message} }
            documents = [question_doc, answer_doc]
            await main_db_client.insert_many(collection=CHAT_COLLECTION, documents=documents)
            return {error_key: True}
    else:
        return None


def check_analysis_type(types:list):
    if all(x == types[0] for x in types): # types 내 모든 값들이 같다?
        return False
    else:
        return True


async def save_fixed_message(fixed_answer, memory_db_client: RedisClient, main_db_client: MongoClient, session_key:str, info:dict=None):
    """
    :param fixedAnswer:
    :param RedisClient:
    :return: generator text
    """
    try:
        if fixed_answer == 1:
            question = FIRST_FIXED_QUESTION
            message = FIRST_FIXED_ANSWER
        elif fixed_answer == 2:
            question = SECOND_FIXED_QUESTION
            message = SECOND_FIXED_ANSWER
        elif fixed_answer == 3:
            question = THIRD_FIXED_QUESTION
            message = THIRD_FIXED_ANSWER
        else:
            logging.error(f"[helper.question.save_fixed_message] fixed answer should be 1, 2 or 3. but fixedAnswer is {fixed_answer}. Check it again")
            raise Exception

        question_redis_format = make_redis_format(question, "human")
        message_redis_format = make_redis_format(message, "ai")

        await memory_db_client.rpush(session_key, question_redis_format)
        await memory_db_client.rpush(session_key, message_redis_format)
        await memory_db_client.set_expire(session_key, REDIS_EXPIRE_TIME)

        input_question_data = mongo_format(session_key, "ai", question, info)
        result = await main_db_client.insert_one(collection="solomonChatHistory", document=input_question_data)
        info["cid"] = str(result.inserted_id)
        input_answer_data = mongo_format(session_key, "human", message, info)
        await main_db_client.insert_one(collection="solomonChatHistory", document=input_answer_data)

    except DBError as e:
        logging.info(f"[helper.question.save_fixed_message] 🔴 DBError: {e}")
        raise DBError(e)
    except MemoryDBError as e:
        logging.info(f"[helper.question.save_fixed_message] 🔴 MemoryDBError: {e}")
        raise MemoryDBError(e)
    except Exception as e:
        logging.info(f"[helper.question.save_fixed_message] 🔴 error: {e}")
        raise e


async def make_fixed_message(fixed_answer):
    try:
        await asyncio.sleep(2) # 생각하는 척 하기
        if fixed_answer == 1:
            message = FIRST_FIXED_ANSWER
        elif fixed_answer == 2:
            message = SECOND_FIXED_ANSWER
        elif fixed_answer == 3:
            message = THIRD_FIXED_ANSWER
        else:
            logging.error(f"[helper.question.save_fixed_message] fixed answer should be 1, 2 or 3. but fixedAnswer is {fixed_answer}. Check it again")
            raise Exception

        for m in message:
            await asyncio.sleep(0.025)
            yield m

    except Exception as e:
        logging.info(f"[helper.question.make_fixed_message] 🔴 error: {e}")
        raise e


def make_redis_format(message:str, role:str):
    return str({"message": message, "role": role})


def mongo_format(session_key, role, message, extra:dict=None):
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
    return form


async def make_error_message(streaming:bool=None, agent:str=None, **kwargs):
    """
    make streaming error message
    """
    streaming = streaming or False
    agent = agent or ""


    message = "알 수 없는 에러가 발생했습니다. 담당자에게 말씀해주시면 신속히 처리하겠습니다. 감사합니다."
    if kwargs.get("agent", None):
        message = "유효한 pathname이 아닙니다."

    if kwargs.get("file"):
        message = "json 파일 내 데이터가 유효한 데이터가 아닙니다. 데이터에 이상한 값이 없는지 확인해주세요."

    if kwargs.get("id"):
        message = "다운로드한 파일에 두 _id가 일치하지 않습니다. 다운로드 받은 파일 확인 후 다시 업로드해주세요."

    if kwargs.get("type", None):
        types = kwargs["type"]
        messages = []
        for enum, t in enumerate(types):
            messages.append(f"type of {enum+1} file: {t}")
        messages.append("\n파일들의 분석타입이 다릅니다. 같은 분석타입을 비교 분석할 수 있도록 동일한 분석타입 파일들을 올려주세요.")
        message = "\n".join(messages)

    if kwargs.get("exception", None):
        message = "알 수 없는 에러가 발생했습니다. 담당자에게 말씀해주시면 신속히 처리하겠습니다. 감사합니다."

    if kwargs.get("noDate", None):
        message = "업로드한 파일에 있는 aireport_id로 조회했을 때 Database에 도큐먼트가 없습니다. 파일 내 _id에 해당하는 데이터가 Database에 있는지 확인해주세요."

    if kwargs.get("noPrefixName"):
        message = "프롬프트 조합을 불러올 수 없습니다. 파일을 새로 받아 시도해주시고 계속 같은 현상이 발생한다면 담당자에게 말씀해주세요."

    if kwargs.get("noAIReportType"):
        message = "DB 내 등록된 type이 없습니다. AIREPORT는 type에 맞게 분석하도록 구성되어있으므로 해당 데이터가 반드시 필요합니다. 파일을 새로 받아 시도해주시고 계속 같은 현상이 발생한다면 담당자에게 말씀해주세요."

    if kwargs.get("notSupportedFileType"):
        message = "지원하지 않는 파일 형태입니다. json, txt를 넣어주세요."

    if kwargs.get("noBefore"):
        message = "먼저 데이터를 업로드해 AI-REPORT를 만들어주세요. DOCENT 모드는 만들어진 AIREPORT에 대해 챗으로 질문하고 답을 얻는 기능입니다. 따라서, 먼저 AI-REPORT를 만들어주셔야해요!"

    if kwargs.get("mashup"):
        message = "mashup은 결과가 있는 ObjectId로만 가능합니다. 업로드한 파일 내 id에 결과가 없는 파일이 있습니다. mashup은 결과 데이터를 결합하는 것이기 때문에 사전에 보내주신 document id에 결과 데이터가 존재해야합니다. 확인 후 다시 업로드해주시길 바랍니다."

    if kwargs.get("noQuestion"):
        message = "업로드한 파일 내 데이터에 결과가 없습니다. 확인 후 다시 업로드해주시길 바랍니다."

    if kwargs.get("notReport"):
        message = "업로드한 파일들 중 REPORT 본문이 없는게 있습니다. 데이터 확인 후 다시 MASHUP 동작시켜주시기 바랍니다."

    if kwargs.get("notSummary"):
        message = "업로드한 파일들 중 SUMMARY 요약문이 없는게 있습니다. 데이터 확인 후 다시 MASHUP 동작시켜주시기 바랍니다."

    if kwargs.get("mashupSame"):
        message = "MASHUP 요청한 두 보고서 타입이 같습니다. MASHUP은 다른 타입의 보고서 두개를 섞는 케이스입니다. 타입 확인하시고 다시 시도해주세요."

    if kwargs.get("LLMError"):
        message = "죄송합니다. 에러가 발생해 답변을 제공할 수 없습니다. 계속 같은 메세지를 받으신다면 담당자에게 연락주시면 감사하겠습니다."

    if kwargs.get("isNotSetReportKR"):
        message = ERR_REPORT_CHAT_KR
    if kwargs.get("isNotSetReportEN"):
        message = ERR_REPORT_CHAT_EN
    if kwargs.get("isNotSetReportJA"):
        message = ERR_REPORT_CHAT_JA

    if kwargs.get("notSchemaURL"):
        message = NOT_SCHEMA_URL_KR
    if kwargs.get("notSchemaURLEN"):
        message = NOT_SCHEMA_URL_EN
    if kwargs.get("notSchemaURLJA"):
        message = NOT_SCHEMA_URL_JP

    if agent in MESSAGE_STRUCTURE_LIST:
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
        }
        message = orjson.dumps(response)

    if streaming:
        if isinstance(message, bytes):
            yield message
        else:
            for m in message:
                await asyncio.sleep(0.025)
                yield m
    else:
        yield message


async def helper_get_reportchat_data(main_db_client:MongoClient, payload:getReportChatDatasPayload):
    try:
        # set filter
        filter = {
            "orgId" : {"$exists" : False},
            "reportS3Path" : True,
        }
        if hasattr(payload, "userId"):
            filter["userId"] = payload.userId
        if hasattr(payload, "reportId") and isinstance(payload.reportId, str):
            filter["_id"] = ObjectId(payload.reportId)
        if hasattr(payload, "domain"):
            filter["domain"] = payload.domain
        filter["orgId"] = {"$exists" : False}
        page = getattr(payload, "page", 1)
        page_size = getattr(payload, "pageSize", 10)
        skip = (page - 1) * page_size
        limit = page_size

        # io: asyncio.gather()
        cursor = await main_db_client.find(collection="baAIReport", filter=filter, skip=skip, limit=limit)
        count = await main_db_client.count_documents(collection="baAIReport", filter=filter)

        #reform
        data = []
        for row in cursor:
            row["_id"] = str(row["_id"])
            data.append(row)

        return {"data": data, "count": count}

    except DBError as e:
        logging.info(f"[helper.question.helper_get_reportchat_data] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.helper_get_reportchat_data] 🔴 error: {e}")
        raise e


async def helper_insert_init_reportchat_row(main_db_client:MongoClient, session_key:str, payload:insertInitReportchatRowPayload):
    try:
        doc = {
            "agent": payload.agent or "reportchat",
            "date": datetime.now(timezone.utc),
            "role": "ai",
            "message": payload.message,
            "sessionKey": session_key,
            "isInit": True,
            "serviceType": payload.service_type
        }
        if payload.service_type == 'ba':
            doc["baAIReportId"] = payload.report_id
        else:
            doc["beusAIReportId"] = payload.report_id
        document = {**doc, **payload.info} if payload.info else doc
        await main_db_client.insert_one(collection="solomonChatHistory", document=document)
    except DBError as e:
        logging.info(f"[helper.question.helper_insert_init_reportchat_row] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.helper_insert_init_reportchat_row] 🔴 error: {e}")
        raise e


async def helper_insert_error_document(main_db_client:MongoClient, session_key:str, payload:askPayload, error_message:str=None):
    try:
        if not error_message:
            error_message = LANG_EN_ERR_MESSAGE if payload.lang == LANG_EN else LANG_JA_ERR_MESSAGE if payload.lang == LANG_JA else LANG_KO_ERR_MESSAGE

        base_document = {
            "agent": payload.agent,
            "sessionKey": session_key,
            "isError": True,
        }
        base_document = {**base_document, **payload.info} if payload.info else {**base_document, **{"pg": True}}
        question_doc = {**base_document, **{"date": datetime.now(timezone.utc), "role": ROLE_HUMAN, "message": payload.question}}
        answer_doc = {**base_document, **{"date": datetime.now(timezone.utc), "role": ROLE_AI, "message": error_message}}
        documents = [question_doc, answer_doc]
        await main_db_client.insert_many(collection=CHAT_COLLECTION, documents=documents)
    except DBError as e:
        logging.info(f"[helper.question.helper_insert_error_reportchat_row] 🔴 DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.question.helper_insert_error_reportchat_row] 🔴 error: {e}")
        raise e


async def helper_set_report(
        main_db_client:MongoClient,
        s3_client:S3Client,
        memory_db_client:RedisClient,
        session_key:str,
        report_id:list,
        category: str,
        service_type:str
):
    try:
        key = f"rc:{session_key}"
        value = str([
            await report_chat_rag(
                main_db_client=main_db_client,
                s3_client=s3_client,
                aid=aid,
                category=category,
                service_type=service_type
            ) for aid in report_id
        ]).replace("null", "None")
        key_id = f"rc_id:{session_key}"
        value_id = f"{report_id}"

        await memory_db_client.set(key=key, value=value)
        await memory_db_client.set(key=key_id, value=value_id)
        await memory_db_client.set_expire(key=key, time=SET_REPORT_REDIS_EXPIRE_TIME)
        await memory_db_client.set_expire(key=key_id, time=SET_REPORT_REDIS_EXPIRE_TIME)

    except DBError as e:
        logging.error(f"[helper.question.helper_set_report] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"[helper.question.helper_set_report] 🔴 MemoryDBError: {e.message}]")
        raise MemoryDBError(e.message)
    except AWSError as e:
        logging.error(f"[helper.question.helper_set_report] 🔴 AWSError: {e.message}]")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.helper_set_report] 🔴 Exception: {e}")
        raise e


async def helper_reset_report(memory_db_client:RedisClient, old_session_key:str, new_session_key:str):
    try:
        # get data of old session_key
        ids_str = await memory_db_client.get(key=f"rc_id:{old_session_key}")
        report_str = await memory_db_client.get(key=f"rc:{old_session_key}")

        if isinstance(ids_str, str) and isinstance(report_str, str):
            # delete data of old session_key
            await memory_db_client.delete(key=f"rc:{old_session_key}")
            await memory_db_client.delete(key=f"rc_id:{old_session_key}")
            await memory_db_client.delete(key=old_session_key)

            # insert data of old session_key to new session_key
            key = f"rc:{new_session_key}"
            value = report_str
            key_id = f"rc_id:{new_session_key}"
            value_id = ids_str
            await memory_db_client.set(key=key, value=value)
            await memory_db_client.set(key=key_id, value=value_id)
            await memory_db_client.set_expire(key=key, time=SET_REPORT_REDIS_EXPIRE_TIME)
            await memory_db_client.set_expire(key=key_id, time=SET_REPORT_REDIS_EXPIRE_TIME)
            return True
        else:
            return False

    except DBError as e:
        logging.info(f"[helper.question.helper_set_report] 🔴 DBError: {e}")
        raise DBError(e)
    except MemoryDBError as e:
        logging.info(f"[helper.question.helper_set_report] 🔴 MemoryDBError: {e}")
        raise MemoryDBError(e)
    except AWSError as e:
        logging.info(f"[helper.question.helper_set_report] 🔴 AWSError: {e}")
        raise AWSError(e)
    except Exception as e:
        logging.info(f"[helper.question.helper_set_report] 🔴 error: {e}")
        raise e


async def report_chat_rag(main_db_client:MongoClient, s3_client, aid:str, category: str, service_type:str):
    try:
        # if category in HEATMAP_LIST:
        if service_type == 'beusable':
            collection = HEATMAPAIREPORT_COLLECTION
        elif service_type == 'geo' or category in [SCHEMACHAT, WHITEPAPER, CXTRENDS]:
            collection = GEOREPORT_COLLECTION
        else:
            collection = "baAIReport"
        document = await main_db_client.find_one(collection=collection, filter={"_id": ObjectId(aid) if isinstance(aid, str) else aid})

        del_keys = [
            "captureStatus",
            "captureS3Path",
            "captureDate",
            "dataStatus",
            "dataS3Path",
            "dataDate",
            "reportStatus",
            "reportS3Path",
            "reportDate",
            "summaryStatus",
            "summaryS3Path",
            "summaryDate",
            "captureList",
            "captureCount",
            "paid",
            "isPromptAdvanced",
            "orgId",
            "paymentId",
            "paymentType",
            "canceled",
            "sysError",
            "reportRetryCount",
            "deleted"
        ]
        result_obj = dict()

        if document['promptType'] == "compare" or document['promptType'] == "mashup":
            if document['promptType'] == "compare":
                org_data_obj = await main_db_client.find(collection="baAIReport", filter={"orgId":str(document['_id']), "deleted": False, "promptType": "single"}, sort=[("regDate", -1)])
            elif document['promptType'] == "mashup":
                org_data_obj = await main_db_client.find(collection="baAIReport", filter={"orgId":str(document['_id']), "deleted": False}, sort=[("mashupIndex", 1)])
            org_list = [org_data for org_data in org_data_obj]

            # data 생성
            orgin_result_list = [] # -> 얘가 data
            for ai_report_obj in org_list:

                if ai_report_obj['promptType'] == "compare":
                    origin_list = await main_db_client.find(collection="baAIReport", filter={"orgId":str(ai_report_obj['_id']), "deleted": False, "promptType": "single"}, sort=[("regDate", -1)])
                    org_list_result = []
                    for org in origin_list:
                        if org.get('dataS3Path'):
                            org_raw_data = await get_s3_content(s3_client, org['dataS3Path'])
                            org['rawData'] = org_raw_data
                        org = {key: value for key, value in org.items() if key not in del_keys}
                        org_list_result.append(org)
                    ai_report_obj['originList'] = org_list_result

                else:
                    data_s3_path = ai_report_obj['dataS3Path']
                    raw_data = await get_s3_content(s3_client, data_s3_path)
                    ai_report_obj['rawData'] = raw_data
                ai_report_obj = {key: value for key, value in ai_report_obj.items() if key not in del_keys}
                orgin_result_list.append(ai_report_obj)

            report_data = None
            summary_data = None

            report_s3_path = document['reportS3Path']
            if report_s3_path:
                report_data = await get_s3_content(s3_client, report_s3_path)

            summary_s3_path = document.get('summaryS3Path', None)
            if summary_s3_path:
                summary_data = await get_s3_content(s3_client, summary_s3_path)

            data = document
            data["originList"] = orgin_result_list

            result_obj['data'] = {key: value for key, value in data.items() if key not in del_keys}
            result_obj['report'] = report_data
            result_obj['summary'] = summary_data if summary_s3_path else None

        else:
            _type = document.get('type')
            data_s3_path = document.get('dataS3Path', None)
            report_s3_path = document.get('reportS3Path', None)
            summary_s3_path = document.get('summaryS3Path', None)
            geo_url = document.get('url', None) if service_type == "geo" else None

            if geo_url:
                result_obj['geo'] = geo_url

            if data_s3_path:
                json_data = await get_s3_content(s3_client, data_s3_path)
                document['rawData'] = json_data
                data = document
                result_obj['data'] = {key: value for key, value in data.items() if key not in del_keys}

            if report_s3_path:
                report_data = await get_s3_content(s3_client, report_s3_path)
                report_data = html_to_markdown(report_data)
                result_obj['report'] = report_data

            if summary_s3_path:
                summary_data = await get_s3_content(s3_client, summary_s3_path)
                result_obj['summary'] = summary_data

        return result_obj

    except DBError as e:
        logging.error(f"[helper.question.report_chat_rag] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except AWSError as e:
        logging.error(f"[helper.question.report_chat_rag] 🔴 AWSError: {e.message}]")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.report_chat_rag] 🔴 Exception: {e}")
        raise e


async def helper_update_rating_to_main_db(main_db_client:MongoClient, ask_id:str, rating:int):
    try:
        await main_db_client.update_one(collection="solomonChatHistory", filter={"ask_id": ask_id}, update={"$set": {"rating": rating}})
    except DBError as e:
        logging.error(f"[helper.question.helper_update_rating_to_main_db] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.helper_update_rating_to_main_db] 🔴 Exception: {e}")
        raise e


async def helper_update_rating_to_memory_db(memory_db_client:RedisClient, session_key:str, ask_id:str, rating:int, history_data:list):
    try:
        is_update = False

        for data in history_data:
            if data.get("id") == ask_id:
                if rating:
                    data["rating"] = rating
                else:
                    del data["rating"]
                is_update = True
                break

        if is_update:
            await memory_db_client.delete(session_key)
            for data in history_data:
                await memory_db_client.rpush(session_key, json.dumps(data))

    except DBError as e:
        logging.error(f"[helper.question.helper_update_rating_to_memory_db] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except MemoryDBError as e:
        logging.error(f"[helper.question.helper_update_rating_to_memory_db] 🔴 MemoryDBError: {e.message}]")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.helper_update_rating_to_memory_db] 🔴 Exception: {e}")
        raise e


async def helper_get_token_for_docent(main_db_client:MongoClient, Id:str, model:str=None):
    try:
        model = model or DOCENT_BASE_MODEL
        docs = await main_db_client.find(
            collection="solomonChatHistory",
            filter={
                "ask_id": Id,
                "agent": {"$in": DOCENT_LIST}
            }
        )
        tokens = 0
        for doc in docs:
            token = doc.get("token", 0)
            tokens += token

        context_windows = CONTEXT_WINDOWS_SIZE[model]
        is_alert = True if tokens / context_windows > 0.95 else False
        return {"alert": is_alert, "token": tokens, "context_windows": context_windows}

    except DBError as e:
        logging.error(f"[helper.question.helper_get_token_for_docent] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.helper_get_token_for_docent] 🔴 Exception: {e}")
        raise e


def make_json_serializable(data):
    for key, value in data.items():
        if isinstance(value, ObjectId):
            data[key] = str(value)
        elif isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            data[key] = make_json_serializable(value)
        elif isinstance(value, list):
            data[key] = [make_json_serializable(v) if isinstance(v, dict) else v for v in value]
    return data


async def helper_get_vendor_and_model_from_database(
        main_db_client:MongoClient,
        category:str
):
    try:
        # get vendor and model from database
        document = await main_db_client.find_one(collection=MODEL_COLLECTION, filter={"agent": category})
        if document and document.get('vendor') and document.get('model'):
            return document["vendor"], document["model"], True
        else:
            return BASE_VENDOR, BASE_MODEL, False
    except DBError as e:
        logging.error(f"[helper.question.helper_get_vendor_and_model_from_database] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.question.helper_get_vendor_and_model_from_database] 🔴 Exception: {e}")
        raise e


def helper_refer_get_service(category:str, server_stage:str):
    if category == REPORTCHAT:
        service = REPORTCHAT_PRODUCTION if server_stage == PRODUCTION else REPORTCHAT_STAGING
    elif category in UXGPT_LIST:
        service = CS_PRODUCTION if server_stage == PRODUCTION else CS_STAGING
    elif category == VOC:
        service = VOC_PRODUCTION if server_stage == PRODUCTION else VOC_STAGING
    elif category in HEATMAP_LIST:
        service = UXHEATMAP_AIREPORT_PRODUCTION if server_stage == PRODUCTION else UXHEATMAP_AIREPORT_STAGING
    else:
        service = "solomon"
    return service


def get_public_url(s3_path, region=None):
    region = region or 'ap-northeast-2'
    if isinstance(s3_path, str):
        bucket, key = s3_path.split(':')
        return [f"https://{bucket}.s3.{region}.amazonaws.com/{key}"]
    elif isinstance(s3_path, (tuple, list)):
        results = list()
        for path in s3_path:
            bucket, key = path.split(':')
            results.append(f"https://{bucket}.s3.{region}.amazonaws.com/{key}")
        return results


def detect_mixed_language(text: str):
    """언어별 문자 비율로 판단"""
    try:
        # 각 언어 문자 개수 세기
        ko_chars = len(re.findall(r'[가-힣]', text))
        ja_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text))
        en_chars = len(re.findall(r'[a-zA-Z]', text))

        total = ko_chars + ja_chars + en_chars

        if total == 0:
            return "mixed"

        max_count = max(ko_chars, ja_chars, en_chars)

        # 50% 이상이면 해당 언어로 판별
        if ko_chars == max_count:
            return LANG_KO
        elif ja_chars == max_count:
            return LANG_JA
        else:
            return LANG_EN
    except Exception as e:
        logging.error(f"[helper.question.detect_mixed_language] question: {text} | return 'mixed'")
        return "mixed"


async def helper_get_conversation_history_from_redis(memory_db_client:RedisClient, session_key:str):
    try:
        conversations_from_redis = await memory_db_client.lrange(session_key, 0, -1)
        conversations_decode = decode_data_from_redis(conversations_from_redis)
        result = parse_conv_data_for_viewer(conversations_decode)
        return result
    except MemoryDBError as e:
        logging.error(f"session_key: {session_key} | [helper.question.helper_get_conversation_history_from_redis] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"session_key: {session_key} | [helper.question.helper_get_conversation_history_from_redis] 🔴 Exception: {e}")
        raise e


def decode_data_from_redis(list_data):
    """
    레디스에서 가져온 데이터를 json으로 잘 전달해주기 위한 함수
    - 레디스 데이터는 리스트 내 문자 데이터로 구성
    - 리스트에서 문자 데이터("{key: value}") 하나하나 뽑아서 json으로 변경
    - 해당 데이터를 다시 리스트에 담아 리턴
    """
    if len(list_data) == 0:
        result = []
    else:
        try:
            result = list(map(lambda string_data: json.loads(string_data), list_data))
        except:
            result = list(map(lambda string_data: ast.literal_eval(string_data), list_data))
    return result


def parse_conv_data_for_viewer(history_data: list):
    if not history_data:
        return []

    view_history = list()
    for conv in history_data:
        if conv["role"] not in ("human", "ai"):
            continue

        if conv["role"] == "ai":
            # mcp message 구조로 redis에 저장되어 있는 경우 parsing
            if isinstance(conv["message"], str) and conv["message"].startswith("[") and conv["message"].endswith("]"):
                mcp_message_datas = ast.literal_eval(conv["message"])
                iterations = list()
                for mcp_message in mcp_message_datas:
                    items = []
                    if mcp_message.get("thinking"):
                        items.append({'type': 'thinking', 'content': mcp_message['thinking']})
                    if mcp_message.get('tool_name'):
                        tool_text = mcp_message['tool_text']
                        try:
                            tool_text = json.loads(tool_text)
                        except (json.JSONDecodeError, TypeError):
                            pass
                        items.append({'type': 'tool', 'name': mcp_message['tool_name'], 'text': tool_text})
                    if mcp_message.get('text'):
                        items.append({'type': 'text', 'content': mcp_message.get('text')})
                    if mcp_message.get('is_error'):
                        items.append({'type': 'is_error', 'is_error': mcp_message.get('is_error')})

                    iteration = {
                        'items': items,
                        'lastType': 'text',
                    }
                    iterations.append(iteration)

                conv = {
                    'mcpData': {
                        'iterations': iterations,
                        'model': None,
                        'currentIteration': -1
                    },
                    'role': 'ai'
                }
        view_history.append(conv)
    return view_history


def html_to_markdown(html_str):
    try:
        h = html2text.HTML2Text()
        # set options
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0 # 줄바꿈
        h.single_line_break = True

        markdown = h.handle(html_str)
        return markdown
    except Exception as e:
        logging.error(f"[helper.question.html_to_markdown] Exception: {e}")
        raise e
