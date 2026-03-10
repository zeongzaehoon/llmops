import re
import ast
import json
import codecs
from bson import ObjectId
from datetime import datetime, timezone

import requests
import pytz

from client.mongo import MongoClient
from client.pinecone import PineconeClient
from client.redis import RedisClient
from client.aws import S3Client
# from client.groxy import LLMProxyClient
from client.groxy import AsyncLLMProxyClient as LLMProxyClient
from utils.error import *
from utils.constants import *
from utils.vector import get_token_length

from module.llm.dto import LLMArgs

# ==============================
# helper for activate.py
# ==============================
async def make_llmArgs(args:dict) -> LLMArgs:
    """
    make llmArgs in order to seperated Action\n
    - pingpong_mode:bool -> indepth mode Y/n
    - redis_save:bool -> save conversation_history Y/n
    """
    try:
        # insert_mongo dict 생성
        insert_mongo = dict()
        if args.get("filename"):
            insert_mongo["filename"] = args["filename"]
        if args.get("aireportId"):
            insert_mongo["aireportId"] = args["aireportId"]
        if args.get("aireportType") and not args.get("docent_mode"):
            insert_mongo["aireportType"] = args["aireportType"]
        if args.get("info_eagle"):
            insert_mongo = {**insert_mongo, **args["info_eagle"]}
        if args.get("info_user"):
            insert_mongo = {**insert_mongo, **args["info_user"]}

        # capture_status 체크
        capture_status = None
        if args.get("aireportType") and not args.get("docent_mode"):
            capture_status = await capture_image_checker(args["main_db_client"], args["aireportId"])

        # LLMArgs 객체 생성
        llmArgs = LLMArgs(
            # server stage
            server_stage=args.get("server_stage"),

            # default user data
            session_key=args.get("session_key"),
            agent=args.get("agent"),

            # client object
            llm_proxy_client=args.get("llm_proxy_client"),
            main_db_client=args.get("main_db_client"),
            memory_db_client=args.get("memory_db_client"),
            vector_db_client=args.get("vector_db_client"),
            s3_client=args.get("s3_client"),
            message_client=args.get("message_client"),

            # for llm-proxy
            service=args.get("service"),
            vendor=args.get("vendor"),
            model=args.get("model"),
            question=args.get("question"),

            # others
            redis_save=args.get("agent") in CONV_HIST_LIST,
            indepth=bool(args.get("indepth")),
            lang=args.get("lang"),
            aireportId=args.get("aireportId"),
            aireportType=args.get("aireportType"),
            docent_mode=args.get("docent_mode", False),
            test=args.get("test", False),
            capture_status=capture_status,
            start_time=args.get("start_time"),
            init_date=args.get("init_date"),
            images=args.get("images"),
            filename=args.get("filename"),
            references=args.get("references"),
            mail=args.get("mail"),
            insert_id=args.get("insert_id"),
            is_report_chat_init=args.get("is_report_chat_init", False),
            ask_id=args.get("ask_id"),
            roleNameList=args.get("roleNameList"),
            roleNameListForPlus=args.get("roleNameListForPlus"),
            info_eagle=args.get("info_eagle"),
            info_user=args.get("info_user"),
            keyword_for_vector=args.get("keyword_for_vector"),
            s3_save=args.get("s3_save"),
            insert_mongo=insert_mongo,
            streaming=args.get("streaming", True),
            dashboard_data=args.get("dashboard_data"),
        )

        return llmArgs

    except DBError as e:
        logging.error(f"[module.llm.helper.make_llmArgs] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.make_llmArgs] 🔴 Exception: {e}")
        raise e


async def capture_image_checker(main_db_client:MongoClient, id):
    try:
        cursor = await main_db_client.find_one(collection="baAIReport", filter={"_id": ObjectId(id)})
        analysis_type = cursor["type"]
        capture_status = cursor["captureStatus"]
        capture_s3_path = cursor["captureS3Path"]
        if capture_status == "complete" and capture_s3_path:
            logging.info(f"===========capture_image_checker: capture is completed and new row({id}) already has capture.")
            return False
        else:
            ref_aid = str(cursor["refAid"][0])
            query_original = {"_id": ObjectId(ref_aid)}
            cursor_original = await main_db_client.find_one(collection="baAIReport", filter=query_original)
            analysis_type_original = cursor_original["type"]
            capture_list = cursor_original.get("captureList")
            capture_count = cursor_original.get("captureCount")
            capture_status_original = cursor_original["captureStatus"]
            capture_s3_path_original = cursor_original["captureS3Path"]

            # 데이터가 꼬여있으면 그냥 넘어가. 대신 로그를 남겨두자.
            if analysis_type != analysis_type:
                logging.info(f"===========capture_image_checker: original type: {ref_aid} and new row type: {id} are diffrent. check it!")
                return True
            if not capture_count or not capture_list:
                logging.info(f"===========capture_image_checker: _id={ref_aid}, original captureList or original captureCount is None. check it!")
                return True
            if analysis_type_original == "journey":
                if capture_status_original == 'complete' and capture_count == 4:
                    major = capture_list.get("major")
                    rollback = capture_list.get("rollback")
                    reload = capture_list.get("reload")
                    drop = capture_list.get("drop")
                    if major and rollback and reload and drop and len(major) > 0 and len(major) > 0 and len(major) > 0 and len(major) > 0:
                        filter ={"_id": ObjectId(id)}
                        update = {"captureStatus": "complete", "captureS3Path": capture_s3_path_original}
                        await main_db_client.update_one(collection="baAIReport", filter=filter, update={'$set': update})
                        return False
                else:
                    logging.info(f"===========capture_image_checker: _id={ref_aid} capture is complete. check it!")
                    return True
            elif analysis_type_original == "trend" or analysis_type_original == "journey":
                if capture_status_original == 'complete' and capture_count == 1:
                    all = capture_list.get("all")
                    if all and len(all) > 0:
                        filter ={"_id": ObjectId(id)}
                        update = {"captureStatus": "complete", "captureS3Path": capture_s3_path_original}
                        await main_db_client.update_one(collection="baAIReport", filter=filter, update={'$set': update})
                        return False
                else:
                    logging.info(f"===========capture_image_checker: _id={ref_aid} capture is complete. check it!")
                    return True

    except DBError as e:
        logging.error(f"[module.llm.helper.capture_image_checker] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.capture_image_checker] 🔴 Exception: {e}")
        raise e


async def get_system_prompt(main_db_client:MongoClient, category:str, roleNameList:list, roleNameListForPlus:list):
    """
    get prompt from mongo
    """
    try:
        prompt_category = get_prompt_category(category) #TODO@jaehoon: make it simple by using list.index(PINGPONG_INDEX)
        # not indepth:
        if not roleNameListForPlus:
            if roleNameList:
                tasks = [
                    get_prompt_from_mongo(main_db_client, agent=prompt_category, roleName=roleName)
                    for roleName in roleNameList
                ]

                results = await asyncio.gather(*tasks)

                modulePrompts = [result[1] for result in results]
                pid = [str(result[0]) for result in results]
                prompt = "\n\n".join(modulePrompts)
            else:
                prompt_result = await get_prompt_from_mongo(main_db_client, agent=prompt_category)
                prompt = prompt_result[1]
                pid = str(prompt_result[0])

        else:
            # 비동기 작업을 저장할 리스트
            base_tasks = []
            indexes = []
            ping_pong_index = None
            for enum, roleName in enumerate(roleNameList):
                if roleName != PINGPONG_INDEX:
                    task_coroutine = get_prompt_from_mongo(main_db_client, agent=prompt_category, kind="prompt", roleName=roleName)
                    base_tasks.append(task_coroutine)
                    indexes.append(enum)
                else:
                    ping_pong_index = enum

            # 비동기 작업 실행
            results = await asyncio.gather(*base_tasks)

            # 결과 정리
            module_prompts = [None] * len(roleNameList)
            base_pid = [None] * len(roleNameList)

            # PINGPONG_INDEX 위치에 플레이스홀더 설정
            if ping_pong_index is not None:
                module_prompts[ping_pong_index] = PINGPONG_INDEX
                base_pid[ping_pong_index] = PINGPONG_INDEX

            # 결과 할당
            for i, enum in enumerate(indexes):
                result = results[i]
                module_prompts[enum] = result[1]
                base_pid[enum] = str(result[0])

            # pingpong 프롬프트 작업 준비
            pingpong_tasks = [
                get_prompt_from_mongo(main_db_client, agent=prompt_category, kind="prompt", roleName=roleName)
                for roleName in roleNameListForPlus
            ]
            # 요약 프롬프트 필요한 경우 추가
            summary_task = None
            if len(roleNameListForPlus) == 1:
                summary_task = get_prompt_from_mongo(main_db_client, agent=prompt_category, kind="prompt", roleName="summary")
                all_tasks = pingpong_tasks + [summary_task]
            else:
                all_tasks = pingpong_tasks

            # 모든 작업 병렬 실행
            all_results = await asyncio.gather(*all_tasks)

            # 결과 처리
            pingpong_results = all_results[:len(pingpong_tasks)]

            prompt = []
            pid = []

            for result in pingpong_results:
                # pingpong 결과 처리
                temp_module_prompts = module_prompts.copy()
                temp_base_pid = base_pid.copy()

                # pingpong 프롬프트 삽입
                temp_module_prompts[ping_pong_index] = result[1]
                temp_base_pid[ping_pong_index] = str(result[0])

                # 최종 프롬프트 결합
                base_prompt = '\n\n'.join(temp_module_prompts)
                prompt.append(base_prompt)
                pid.append(temp_base_pid)

            # 요약 프롬프트 처리
            if len(roleNameListForPlus) == 1 and summary_task:
                summary_result = all_results[-1]
                prompt.append(summary_result[1])
                pid.append([str(summary_result[0])])

        return prompt, pid

    except DBError as e:
        logging.error(f"[module.llm.helper.get_system_prompt] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_system_prompt] 🔴 Exception: {e}")
        raise e


async def get_query_prompt(llmArgs:LLMArgs):
    try: # main_db_client:MongoClient, category, question=None

        prompt_category = get_prompt_category(llmArgs.agent)
        if llmArgs.agent in QUERY_CATEGORY_PROMPT_LIST:
            filter = {"agent": prompt_category, "kind": "query"}
            sort = [("date", -1)]
            result = await llmArgs.main_db_client.find_one(collection=PROMPT_COLLECTION, filter=filter, sort=sort)
            pinecone_query = ast.literal_eval(result["prompt"]) if result["prompt"][0] == '[' and result["prompt"][-1] == ']' else result["prompt"]
            qid = str(result["_id"])
        elif llmArgs.agent == VOC:
            pinecone_query = llmArgs.keyword_for_vector
            qid = None
        else:
            pinecone_query = llmArgs.question
            qid = None
        return (pinecone_query, qid)

    except DBError as e:
        logging.error(f"[module.llm.helper.get_query_prompt] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_query_prompt] 🔴 Exception: {e}")
        raise e


async def get_prompt_from_mongo(main_db_client:MongoClient, **kwargs:dict):
    try:
        filter = kwargs
        sort = [("date", -1)]
        result = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter=filter, sort=sort)
        return [result["_id"], result["prompt"]]

    except DBError as e:
        logging.error(f"[module.llm.helper.get_prompt_from_mongo] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_prompt_from_mongo] 🔴 Exception: {e}")
        raise e


def get_prompt_category(category):
    # contactUs and UXGPT should be same.
    try:
        if category in UXGPT_LIST:
            prompt_category = CS
        elif category in SWCAG_LIST:
            prompt_category = SWCAG
        else:
            prompt_category = category
        return prompt_category
    except Exception as e:
        logging.error(f"[module.llm.helper.get_prompt_category] 🔴 Exception: {e}")
        raise e


async def get_report_and_data_from_main_db(s3_client:S3Client, main_db_client:MongoClient, target_id_list:list, from_:str=None):
    try:
        target_ids = [ObjectId(id) for id in target_id_list]
        filter = {"_id": {"$in": target_ids}}
        result = await main_db_client.find(collection="baAIReport", filter=filter)

        report = list()
        data = list()
        for doc in result:
            id = str(doc.get("_id"))
            report_path = doc.get("reportS3Path")
            # data_path = doc.get("dataS3Path")
            bucket, key = report_path.split(':')
            download_file = await s3_client.download_file(bucket=bucket, key=key)
            report_ = download_file.decode('utf-8')
            # bucket, key = data_path.split(':')
            # data_ = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
            if from_:
                refer_row = {"subject": doc.get("title"), "content": report_, "category": from_, "url": str(doc.get("_id"))}
            else:
                refer_row = {"id": id, "report": report_, "regDate": doc.get("regDate"), "startDate": doc.get("startDate"), "endDate": doc.get("endDate")}
            report.append(refer_row)
            # data.append({"id": id, "data": data_, "regDate": doc.get("regDate"), "startDate": doc.get("startDate"), "endDate": doc.get("endDate")})

        return (str(report), str(data)) if not from_ else report


    except DBError as e:
        logging.error(f"[module.llm.helper.get_report_and_data_from_main_db] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except AWSError as e:
        logging.error(f"[module.llm.helper.get_report_and_data_from_main_db] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_report_and_data_from_main_db] 🔴 Exception: {e}")
        raise e



async def get_retrieval_data_for_rag(llm_proxy_client:LLMProxyClient, vector_db_client:PineconeClient, vector_query, k:int=4, service:str=DEFAULT, init_date=None):
    try:
        common_data = None
        if init_date:
            common_data = get_common_sense_data(init_date)
        if isinstance(vector_query, list):
            fetchRes = await vector_db_client.fetch(vector_query)
            docs = [doc for doc in fetchRes.vectors.values()]
            return {"retrieval_data": format_docs(docs, common_data), "rid": get_rid_list(docs)}
        elif isinstance(vector_query, str):
            vector = await llm_proxy_client.embeddings(text=vector_query, service=service)
            docs = await vector_db_client.find(vector, k, filter={"isOn": True})
            return {"retrieval_data": format_docs(docs, common_data), "rid": get_rid_list(docs)}
        elif vector_query is None:
            return {"retrieval_data": [], "rid": []}

    except VectorDBError as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_rag] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except LLMProxyError as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_rag] 🔴 LLMProxyError: {e.message}")
        raise LLMProxyError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_rag] 🔴 Exception: {e}")
        raise e


async def get_retrieval_data_for_view(llm_proxy_client:LLMProxyClient, vector_db_client:PineconeClient, question, service, k:int=4):
    try:
        if isinstance(question, list):
            fetchRes = await vector_db_client.fetch(question)
            docs = [doc for doc in fetchRes.vectors.values()]
        else:
            vector = await llm_proxy_client.embeddings(text=question, service=service)
            docs = await vector_db_client.find(vector, k, filter={"isOn": True})
        result = [
            {
                'category': "solomon" if document.metadata.get("postGroupingCodeId") == 7 else "notice" if document.metadata.get("postGroupingCodeId") == 3 else document.metadata.get("source", None),
                'subject': document.metadata.get('chapter', None) or document.metadata.get('subject', None),
                'content': document.metadata.get('text', None) or document.page_content,
                'url': document.metadata.get('url', None),
                'imageURL': document.metadata.get('imageURL', None),
                'contentAdmin': document.metadata.get('contentAdmin', None),
            } for document in docs
        ]
        return result

    except VectorDBError as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_view] 🔴 VectorDBError: {e.message}")
        raise VectorDBError(e.message)
    except LLMProxyError as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_view] 🔴 LLMProxyError: {e.message}")
        raise LLMProxyError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_retrieval_data_for_view] 🔴 Exception: {e}")
        raise e


async def get_conversation_history_for_view(memory_db_client:RedisClient, session_key:str):
    try:
        conversations_from_redis = await memory_db_client.lrange(session_key, 0, -1)
        conversations_decode = decode_data_from_redis(conversations_from_redis)
        result = parse_conv_data_for_viewer(conversations_decode)
        return result
    except MemoryDBError as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.get_conversation_history_for_view] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.get_conversation_history_for_view] 🔴 Exception: {e}")
        raise e


async def get_conversation_history_for_llm(memory_db_client:RedisClient, session_key:str):
    """Redis에서 대화이력 가져오기"""
    try:
        count = await memory_db_client.llen(session_key)
        if count == 0:
            conversations = ''
        elif count > 40:
            conversations = await memory_db_client.lrange(session_key, -40, -1)
        else:
            conversations = await memory_db_client.lrange(session_key, 0, -1)

        conversation_history = [conversation for conversation in decode_data_from_redis(conversations)]
        return conversation_history

    except MemoryDBError as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.get_conversation_history_for_llm] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.get_conversation_history_for_llm] 🔴 Exception: {e}")
        raise e


def format_docs(docs, common_data:list=None):
    documents = list()
    for document in docs:
        image_url = document.metadata.get("imageURL")
        is_show = bool(document.metadata.get("isShow", False))
        content = document.metadata.get("text","")
        title = document.metadata.get("subject")
        contentAdmin = document.metadata.get("contentAdmin")

        if is_show:
            page_content = {
                "title": title,
                "content": content
            }
            if contentAdmin:
                page_content["contentAdmin"] = contentAdmin
            if image_url:
                page_content["imageURL"] = image_url
        else:
            page_content = {}

        documents.append(page_content)

    if common_data:
        documents.extend(common_data)

    return str(documents)


def get_rid_list(docs):
    return [document['id'] for document in docs]


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
    view_history = list()
    for conv in history_data:
        if conv["role"] == "human":
            view_history.append(conv)
        elif conv["role"] == "ai":
            if isinstance(conv["message"], str) and conv["message"][0] == "[" and conv["message"][-1] == "]":
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
            else:
                view_history.append(conv)
    return view_history


async def get_report_datas(main_db_client, s3_client, target_id_list):
    try:
        report = list()
        data = list()
        for id in target_id_list:
            report_path = main_db_client.find_one(collection="baAIReport", filter={"_id": ObjectId(id)})["reportS3Path"]
            data_path = main_db_client.find_one(collection="baAIReport", filter={"_id": ObjectId(id)})["dataS3Path"]
            bucket, key = report_path.split(':')
            report_ = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
            report.append(report_)
            bucket, key = data_path.split(':')
            data_ = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
            data.append(data_)
        return (report, data)

    except DBError as e:
        logging.info(f"[llm.helper.get_report_datas] 🔴 DBError: {e}")
        raise DBError(e)
    except AWSError as e:
        logging.info(f"[llm.helper.get_report_datas] 🔴 AWSError: {e}")
        raise AWSError(e)
    except Exception as e:
        logging.info(f"[llm.helper.get_report_datas] 🔴 Exception: {e}")
        raise e


async def report_chat_rag(main_db_client:MongoClient, s3_client:S3Client, aid:str):
    try:
        ai_report = await main_db_client.find_one(collection="baAIReport", filter={"_id": ObjectId(aid) if isinstance(aid, str) else aid})

        result_obj = dict()

        if ai_report['promptType'] == "compare" or ai_report['promptType'] == "mashup":
            if ai_report['promptType'] == "compare":
                org_data_obj = await main_db_client.find(collection="baAIReport", filter={"orgId":str(ai_report['_id']), "deleted": False, "promptType": "single"}, sort=[("regDate", -1)])
            elif ai_report['promptType'] == "mashup":
                org_data_obj = await main_db_client.find(collection="baAIReport", filter={"orgId":str(ai_report['_id']), "deleted": False}, sort=[("mashupIndex", 1)])
            org_list = [org_data for org_data in org_data_obj]

            # data 생성
            orgin_result_list = [] # -> 얘가 data
            for ai_report_obj in org_list:

                if ai_report_obj['promptType'] == "compare":
                    origin_list = await main_db_client.find(collection="baAIReport", filter={"orgId":str(ai_report_obj['_id']), "deleted": False, "promptType": "single"}, sort=[("regDate", -1)])
                    org_list_result = []
                    for org in origin_list:
                        if org['dataS3Path']:
                            org_raw_data = await get_s3_content(s3_client, org['dataS3Path'])
                            org['rawData'] = org_raw_data
                        org_list_result.append(org)
                    ai_report_obj['originList'] = org_list_result

                else:
                    data_s3_path = ai_report_obj['dataS3Path']
                    raw_data = await get_s3_content(s3_client, data_s3_path)
                    ai_report_obj['rawData'] = raw_data

                orgin_result_list.append(ai_report_obj)

            report_data = None
            summary_data = None

            report_s3_path = ai_report['reportS3Path']
            if report_s3_path:
                report_data = await get_s3_content(s3_client, report_s3_path)

            summary_s3_path = ai_report.get('summaryS3Path', None)
            if summary_s3_path:
                summary_data = await get_s3_content(s3_client, summary_s3_path)

            data = ai_report
            data["originList"] = orgin_result_list

            result_obj['data'] = data
            result_obj['report'] = report_data
            result_obj['summary'] = summary_data if summary_s3_path else None

        else:
            data_s3_path = ai_report['dataS3Path']
            report_s3_path = ai_report['reportS3Path']
            summary_s3_path = ai_report.get('summaryS3Path', None)

            data = None
            report_data = None
            summary_data = None

            if data_s3_path:
                json_data = await get_s3_content(s3_client, data_s3_path)
                ai_report['rawData'] = json_data
                data = ai_report

            if report_s3_path:
                report_data = await get_s3_content(s3_client, report_s3_path)

            if summary_s3_path:
                summary_data = await get_s3_content(s3_client, summary_s3_path)

            result_obj['data'] = data
            result_obj['report'] = report_data
            result_obj['summary'] = summary_data

        return result_obj

    except DBError as e:
        logging.error(f"[module.llm.helper.report_chat_rag] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except AWSError as e:
        logging.error(f"[module.llm.helper.report_chat_rag] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.report_chat_rag] 🔴 Exception: {e}")
        raise e


async def get_s3_content(s3_client:S3Client, s3_path):
    try:
        bucket, key = s3_path.split(':')
        download_file = await s3_client.download_file(bucket=bucket, key=key)
        result = download_file.decode('utf-8')
        return result
    except AWSError as e:
        logging.error(f"[module.llm.helper.get_s3_content] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_s3_content] 🔴 Exception: {e}")
        raise e


def get_common_sense_data(init_date=None):
    try:
        results = []
        if init_date:
            time_info = f"(UTC) {init_date.year}년 {init_date.month}월 {init_date.day}일, {init_date.hour}시 {init_date.minute}분 {init_date.second}초입니다."
            results.append({"title": "현재 UTC 시간", "content": time_info})
        return results

    except Exception as e:
        logging.error(f"[module.llm.helper.get_common_sense_data] 🔴 Exception: {e}")
        raise e


async def get_vendor_and_model(main_db_client: MongoClient, category: str):
    try:
        document = await main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={'agent': category}
        )
        return document["vendor"], document["model"]
    except DBError as e:
        logging.error(f"[module.llm.helper.get_vendor_and_model] 🔴 DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.get_vendor_and_model] 🔴 Exception: {e}")
        raise e


def make_error_message(lang:str = None):
    lang = lang or LANG_KO
    message = LANG_EN_ERR_MESSAGE if lang == LANG_EN else LANG_JA_ERR_MESSAGE if lang == LANG_JA else LANG_KO_ERR_MESSAGE
    for character in message:
        yield character


async def record_err_to_main_db(args: dict):
    main_db_client: MongoClient = args.get("main_db_client")
    if not main_db_client:
        logging.error(f"[module.llm.helper.record_err_to_main_db] main_db_client must be set, but there is not main_db_client")
        raise ValueError

    if args.get("insert_id"):
       await main_db_client.delete_one(CHAT_COLLECTION, {"_id": ObjectId(args["insert_id"])})

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

    await main_db_client.insert_many(CHAT_COLLECTION, documents)


# ==============================
# helper for run.py
# ==============================
def make_human_message(
        question,
        retrieval_data=None,
        language_message=None,
        references=None,
        mail=None,
        selected_report_data=None,
        before_report_question=None,
        before_report_answer=None,
        image_data=None,
        is_report=None,
        dashboard_data=None
):
    result = f"<사용자 질문>\n{question}\n</사용자 질문>" if not is_report else f"<원본 데이터>\n{question}\n</원본 데이터>"
    if before_report_answer:
        result = f"<이전 리포트 내용>\n{before_report_answer}\n</이전 리포트 내용>\n\n\n{result}"
    if before_report_question:
        result = f"<이전 리포트 원본 데이터>\n{before_report_question}\n</이전 리포트 원본 데이터>\n\n\n{result}"
    if image_data:
        result = f"<분석 요청한 이미지 URL>\n{image_data}\n</분석 요청한 이미지 URL>\n\n\n{result}"
    if retrieval_data:
        result = f"<참조 데이터>\n{retrieval_data}\n</참조 데이터>\n\n\n{result}"
    if language_message:
        result = result + f"\n\n\n<답변 언어>\n{language_message}\n</답변 언어>"
    if references:
        result = f"<메일 쓰레드>\n{references}</메일 쓰레드>\n\n\n{result}"
    if mail:
        result = f"<메일 본문>\n{mail}\n</메일 본문>\n\n\n{result}"
    if selected_report_data:
        result = f"<보고서 데이터>\n{selected_report_data}\n</보고서 데이터>\n\n\n{result}"
    if dashboard_data:
        result = f"<대시보드 데이터>\n{dashboard_data}\n</대시보드 데이터>\n\n\n{result}"

    return result


async def save_to_memory_db(
    memory_db_client:RedisClient,
    session_key:str,
    message:str,
    role:str,
    ask_id:str=None
):
    try:
        data_redis = redis_format(role=role, message=message, ask_id=ask_id)
        await memory_db_client.rpush(session_key, data_redis)
        await memory_db_client.set_expire(session_key, REDIS_EXPIRE_TIME)
    except MemoryDBError as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.save_to_memory_db] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.save_to_memory_db] 🔴 Exception: {e}")
        raise e


# specific function for aireport page
async def save_answer_to_memory_db(
        memory_db_client:RedisClient,
        session_key:str,
        message:str,
        role:str,
        report_id:str,
        report_type:str,
        is_report_target:bool,
        is_mashup_target:bool,
        is_summary_target:bool,
        ask_id:str=None,
):

    try:
        answer_data_redis = redis_format(
            role=role,
            message=message,
            report_id=report_id,
            report_type=report_type,
            report_target=is_report_target,
            mashup_target=is_mashup_target,
            summary_target=is_summary_target,
            ask_id=ask_id
        )
        await memory_db_client.rpush(session_key, answer_data_redis)
        await memory_db_client.set_expire(session_key, REDIS_EXPIRE_TIME)

    except MemoryDBError as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.save_answer_to_memory_db] 🔴 MemoryDBError: {e.message}")
        raise MemoryDBError(e.message)
    except Exception as e:
        logging.error(f"session_key: {session_key} | [module.llm.helper.save_answer_to_memory_db] 🔴 Exception: {e}")
        raise e


def redis_format(
        message:str,
        role:str=None,
        report_id:str=None,
        report_type:str=None,
        report_target:bool=False,
        mashup_target:bool=False,
        summary_target:bool=False,
        ask_id:str=None
):
    """Redis input data format"""
    try:
        form = {
            "message": message,
        }
        if role:
            form["role"] = role
        if report_id:
            form["reportId"] = report_id
        if report_type:
            form["reportType"] = report_type
        if report_target:
            form["reportReady"] = True
        if mashup_target:
            form["type"] = "fullReport"
            form["reportReady"] = True
        if summary_target:
            form["type"] = "mainReport"
            form["reportReady"] = True
        if ask_id != None and role == "ai":
            form["id"] = ask_id
            form["rating"] = None
        return str(form)

    except Exception as e:
        logging.info(f"[llm.helper.redis_format] 🔴 Exception: {e}")
        raise e


def decode_redis_format_for_gpt(datas:list):
    """langchain -> gpt API 변환에 따라, 포맷 변환 필요"""
    try:
        return [
            {
                "role": "assistant" if data.get("role") == "ai" else "user",
                "content": data.get("message")
            } for data in datas
        ] if datas else None
    except Exception as e:
        logging.error(f"[module.llm.helper.decode_redis_format_for_gpt] 🔴 Exception: {e}")
        raise e


async def save_s3(
    main_db_client:MongoClient,
    s3_client:S3Client,
    s3_save:dict,
    data:str,
    enum:int=None
):
    try:
        '''
        ### ARGS
        1. if enum == 2: save summary
        2. if enum == 1 or None: save report
        '''
        aireport_id = s3_save['id']
        type_ = s3_save['type']
        parent_sid = s3_save['parentSid']
        reg_date = s3_save['regDate']
        start = s3_save['startDateStr']
        end = s3_save['endDateStr']
        start_format = start.replace('-', '')[2:]
        end_format = end.replace('-', '')[2:]
        name = "summary" if enum == 2 else "report"
        file_name = f'{parent_sid}_{type_}_{start_format}_{end_format}_{name}.txt'
        s3_path = f'journeymap/docent/{reg_date}/{parent_sid}/{aireport_id}/{file_name}'
        await s3_client.upload_file(bucket=BA_AWS_BUCKET_NAME, key=s3_path, file_data=json.dumps(data, ensure_ascii=False))
        filter = {"_id":ObjectId(aireport_id)}
        update = {"$set":{
            "summaryDate": pytz.timezone('Asia/Seoul').localize(datetime.now()),
            "summaryStatus": "complete",
            "summaryS3Path": f"{BA_AWS_BUCKET_NAME}:{s3_path}"
        }} if enum == 2 else {"$set":{
            "reportDate": pytz.timezone('Asia/Seoul').localize(datetime.now()),
            "reportStatus": "complete",
            "reportS3Path": f"{BA_AWS_BUCKET_NAME}:{s3_path}"
        }}
        await main_db_client.update_one(collection="baAIReport", filter=filter, update=update)

    except DBError as e:
        logging.error(f"[module.llm.helper.save_s3] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except AWSError as e:
        logging.error(f"[module.llm.helper.save_s3] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.save_s3] 🔴 Exception: {e}")
        raise e


async def send_slack_message(message, channel=None):
    SLACK_API_URL = 'https://slack.com/api/chat.postMessage'
    msg_obj = {
        'channel': '#alert' if channel is None else channel,
        'text': message
    }
    header = {
        'Authorization': 'Bearer {}'.format(os.getenv('SLACK_TOKEN')),
        'Content-Type': 'application/json'
    }
    try:
        res = await requests.post(SLACK_API_URL, json=msg_obj, headers=header)
        logging.info('res: {}'.format(res.json()))
        return res
    except Exception as e:
        logging.error(f"[module.llm.helper.send_slack_message] 🔴 Exception: {e}")


def write_log_for_debug_message(system_message=None, conversation_history=None, human_message=None):
    logging.info("*"*100)
    logging.info(f"[시스템 프롬프트] {system_message}")
    logging.info("*"*100)
    logging.info(f"[대화 이력] {conversation_history}")
    logging.info("*"*100)
    logging.info(f"[사용자 프롬프트] {human_message}")
    logging.info("*"*100)


def remove_code_blocks(llmArgs:LLMArgs):
    pattern = r'```[\w]*\n?(.*?)```'
    llmArgs.answer = re.sub(pattern, r'\1', llmArgs.answer, flags=re.DOTALL).strip()


def remove_escape_in_html_str(llmArgs:LLMArgs):
    is_html = llmArgs.answer.lstrip().startswith('<!DOCTYPE') or llmArgs.answer.lstrip().startswith('<html')
    if not is_html:
        llmArgs.answer = llmArgs.answer.split('<!DOCTYPE html>')[-1].split('</html>')[0]
        llmArgs.answer = f'<!DOCTYPE html>{llmArgs.answer}</html>'
        if '\\u' in llmArgs.answer or '\\x' in llmArgs.answer or '\\n' in llmArgs.answer:
            llmArgs.answer = codecs.decode(llmArgs.answer, 'unicode_escape')


# ==============================
# helper for model.py
# ==============================
async def save_answer_to_main_db(
    main_db_client:MongoClient,
    session_key:str,
    message:str,
    model:str,
    insert_mongo:dict,
    indepth:bool,
    role:str,
    ask_id:str=None,
    service_type:str='ba'
):

    try:
        # save answer
        insert_mongo["token"] = get_token_length(message, model)
        if ask_id:
            insert_mongo["ask_id"] = ask_id
        data_mongo = mongo_format(session_key, role, message, insert_mongo)
        await main_db_client.insert_one(collection="solomonChatHistory", document=data_mongo)
        # save history data
        pid = insert_mongo.get("pid", None)
        qid = insert_mongo.get("qid", None)
        if pid and type(pid) == str:
            filter = {'_id': ObjectId(pid)}
            update = {"$set": {"getResult": True}}
            await main_db_client.update_one(collection=PROMPT_COLLECTION, filter=filter, update=update)

        elif pid and type(pid) == list:
            update_tasks = []
            if indepth:
                pid = [pid for sublist in pid for pid in sublist]
            for pid in pid:
                filter = {'_id': ObjectId(pid)}
                update = {"$set": {"getResult": True}}
                update_tasks.append(main_db_client.update_one(collection=PROMPT_COLLECTION, filter=filter, update=update))
            await asyncio.gather(*update_tasks)

        if qid and type(qid) == str:
            filter = {'_id': ObjectId(qid)}
            update = {"$set": {"getResult": True}}
            await main_db_client.update_one(collection=PROMPT_COLLECTION, filter=filter, update=update)

        elif qid and type(qid) == list:
            update_tasks = []
            if indepth:
                qid = [qid for sublist in qid for qid in sublist]
            for qid in qid:
                filter = {'_id': ObjectId(qid)}
                update = {"$set": {"getResult": True}}
                update_tasks.append(main_db_client.update_one(collection=PROMPT_COLLECTION, filter=filter, update=update))
            await asyncio.gather(*update_tasks)

    except DBError as e:
        logging.error(f"[module.llm.helper.save_answer_to_main_db] 🔴 DBError: {e.message}")
        raise DBError(e.message)
    except AWSError as e:
        logging.error(f"[module.llm.helper.save_answer_to_main_db] 🔴 AWSError: {e.message}")
        raise AWSError(e.message)
    except Exception as e:
        logging.error(f"[module.llm.helper.save_answer_to_main_db] 🔴 Exception: {e}")
        raise e
