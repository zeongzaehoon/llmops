import io
import os
import ast
import json
import logging
import zipfile
from datetime import datetime, timezone
from bson import ObjectId

from fastapi.responses import StreamingResponse

from payload.operation import *
from utils.constants import *
from utils.error import *
from client.mongo import MongoClient, ProductionMongoClient
from client.pinecone import PineconeClient


def make_filter(**kwargs):
    """mongoDB find 조건 쿼리 만드는 함수"""
    filter = {key: value for key, value in kwargs.items() if value != None}
    return filter


def trans_objectid_str(data: dict):
    """BSON ObjectId 값을 문자형태로 변경해 내려주기 위한 함수"""
    data['_id'] = str(data['_id'])
    return data


async def helper_get_version(main_db_client:MongoClient, payload:getVersionPayload):
    try:
        # get data from payload
        category = payload.agent
        kind = payload.kind
        role_name = payload.role_name

        # get data from mongoDB
        collection = get_collection(category, kind)
        filter = make_version_filter(category=category, kind=kind, roleName=role_name)
        sort = [("date", -1)]
        cursor = await main_db_client.find(collection=collection, filter=filter, sort=sort)
        if kind == REFER:
            data = reform_version_refer_cursor(cursor)
        else:
            data = reform_version_cursor(cursor=cursor, category=category, kind=kind)
        return data
    except DBError as e:
        logging.info(f"[helper.operation.helper_get_version] 🔴 Failed to get version data: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_get_version] 🔴 Failed to get version data: {e}")
        raise Exception(e)


def get_vector_db_index(category:str, server_stage:str) -> str:
    if category in UXGPT_LIST:
        vector_db_index = CONTACTUS_INDEX if server_stage == PRODUCTION else CONTACTUS_STAGING_INDEX
    elif category == "reportchat":
        vector_db_index = REPORTCHAT_INDEX
    else:
        vector_db_index = MAIN_INDEX
    return vector_db_index


async def helper_get_data(main_db_client:MongoClient, vector_db_client:PineconeClient, payload:getDataPayload):
    try:
        # get data from payload
        category = payload.agent
        id = payload.id
        kind = payload.kind
        page = payload.page
        if not id:
            id = "670bf833963d3e3d97870364"

        if kind != REFER: #mongoDB에서 데이터 조회
            collection = get_collection(category, kind)
            filter = {'_id':ObjectId(id)}
            cursor = await main_db_client.find_one(collection=collection, filter=filter)
            if collection == PROMPT_COLLECTION:
                data = reform_prompt_cursor(cursor=cursor)
            elif collection == CHAT_COLLECTION:
                data = await reform_chat_cursor(main_db_client=main_db_client, cursor=cursor, category=category, kind=kind)
        else: #Pinecone에서 데이터조회
            ids = [str(id)]
            response = await vector_db_client.fetch(ids=ids)
            data = reform_refer_response(response)

        if kind != RESULT:
            key = get_id(category=category, kind=kind)
            value = str(id) if kind not in [PROMPT, REFER] else {"$in": [str(id)]}
            filter = {key: value, "role":"ai"}
            sort = [("date", -1)] #{"date": -1}
            limit = 5 if page else None
            skip = (page - 1) * limit if page else None
            cursor = await main_db_client.find(collection=CHAT_COLLECTION, filter=filter, sort=sort, skip=skip, limit=limit)
            result_data = reform_result_id_cursor(cursor=cursor, category=category)
            if not result_data:
                value = {"$elemMatch":{"$elemMatch":{"$eq":str(id)}}}
                filter = {key: value, "role":"ai"}
                cursor = await main_db_client.find(collection=CHAT_COLLECTION, filter=filter, sort=sort, skip=skip, limit=limit)
                result_data = reform_result_id_cursor(cursor=cursor, category=category)
            data['result'] = result_data

        return data

    except DBError as e:
        logging.info(f"[helper.operation.helper_get_data] 🔴 Failed to get data: {e}")
        raise DBError(e)
    except VectorDBError as e:
        logging.info(f"[helper.operation.helper_get_data] 🔴 Failed to get data: {e}")
        raise VectorDBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_get_data] 🔴 Failed to get data: {e}")
        raise Exception(e)


async def helper_get_prompt(main_db_client:MongoClient, payload):
    try:
        filter = {'_id': ObjectId(payload.id)}
        cursor = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter=filter)
        data = reform_prompt_cursor(cursor=cursor)
        return data
    except DBError as e:
        logging.info(f"[helper.operation.helper_get_prompt] 🔴 Failed to get prompt: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_get_prompt] 🔴 Failed to get prompt: {e}")
        raise Exception(e)


async def helper_download_question(main_db_client:MongoClient, id:str):
    try:
        filter = {'_id':ObjectId(id)}
        cursor = await main_db_client.find_one(collection=CHAT_COLLECTION, filter=filter)
        question_data = cursor['message']
        filename_data = cursor.get('filename', None) #파일을 업로드했을 때만 값이 존재함. 아니면 None
        filename, filedata, mimetype = make_fileinfo(question_data, filename_data)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        # filedata가 BytesIO 객체인 경우
        if isinstance(filedata, io.BytesIO):
            return StreamingResponse(
                filedata,
                media_type=mimetype,
                headers=headers
            )
        # filedata가 문자열인 경우, BytesIO로 변환
        elif isinstance(filedata, str):
            bytes_io = io.BytesIO(filedata.encode('utf-8'))
            return StreamingResponse(
                bytes_io,
                media_type=mimetype,
                headers=headers
            )

    except DBError as e:
        logging.info(f"[helper.operation.helper_download_question] 🔴 Failed to download question: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_download_question] 🔴 Failed to download question: {e}")
        raise Exception(e)


async def helper_update_memo(main_db_client:MongoClient, payload:updateMemoPayload):
    try:
        id = payload.id
        category = payload.agent
        kind = payload.kind
        memo = payload.memo

        filter = {'_id':ObjectId(id)}
        update = {"$set": {'memo': memo}}
        collection = get_collection(category=category, kind=kind)
        result = await main_db_client.update_one(collection=collection, filter=filter, update=update)
        return result

    except DBError as e:
        logging.info(f"[helper.operation.helper_update_memo] 🔴 Failed to update memo: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_update_memo] 🔴 Failed to update memo: {e}")
        raise Exception(e)


async def helper_deploy_whole(
    production_main_db_client:ProductionMongoClient,
    staging_main_db_client:MongoClient,
    category:str
):
    try:
        # 0.
        deploy_date = datetime.now(timezone.utc)

        # 1. get prompt from staging database
        tasks_1 = [
            staging_main_db_client.find_one(
                collection=PROMPT_COLLECTION,
                filter={'agent': category},
                sort=[("date", -1)]
            ),
            production_main_db_client.find_one(
                collection=PROMPT_COLLECTION,
                filter={"agent": category},
                sort=[("date", -1)]
            )
        ]
        staging_prompt_doc, current_production_prompt_doc = await asyncio.gather(*tasks_1)
        current_production_prompt_doc_id = current_production_prompt_doc["_id"]

        # 2. change date, deploy status
        staging_prompt_doc['date'] = deploy_date
        staging_prompt_doc['deployStatus'] = "green"

        # 3. insert staging doc to production and change status in production
        tasks_2 = [
            # insert new
            production_main_db_client.insert_one(
                collection=PROMPT_COLLECTION,
                document=staging_prompt_doc
            ),
            # update status of old one
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": current_production_prompt_doc_id},
                update={"$set": {"deployStatus": "blue"}}
            )
        ]
        await asyncio.gather(*tasks_2)

    except DBError as e:
        logging.error(f"[helper.operation.helper_deploy_whole] DBError: {e.message}")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.operation.helper_deploy_whole] Exception")
        raise Exception(e)


async def helper_get_deploy_list(production_main_db_client:ProductionMongoClient, staging_main_db_client:MongoClient):
    try:
        # prompt deploy comparison (staging vs production)
        sort = [("date", 1)]
        real_prompt_data = {
            doc['agent']: doc
            for doc in await production_main_db_client.find(
                collection=PROMPT_COLLECTION,
                filter={"deployStatus": "green"},
                sort=sort)
        }
        staging_prompt_data = {
            doc['agent']: doc
            for doc in await staging_main_db_client.find(
                collection=PROMPT_COLLECTION,
                filter={},
                sort=sort)
        }
        update_module_list = [
            category
            for category in staging_prompt_data
            if category not in real_prompt_data or staging_prompt_data[category]['date'] > real_prompt_data[category].get('date', datetime.min)
        ]

        return {
            "update_type_list": [],
            "update_module_list": update_module_list
        }

    except DBError as e:
        logging.info(f"[helper.operation.helper_get_deploy_list] 🔴 Failed to get deploy list: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.helper_get_deploy_list] 🔴 Failed to get deploy list: {e}")
        raise Exception(e)


async def helper_rollback_not_aireport(
    production_main_db_client:ProductionMongoClient,
    category:str
):
    try:
        deploy_date = datetime.now(timezone.utc)

        # 1. get blue status document, green status document
        tasks_1 = [
            production_main_db_client.find_one(
                collection=PROMPT_COLLECTION,
                filter={"deployStatus": "blue", "agent": category}
            ),
            production_main_db_client.find_one(
                collection=PROMPT_COLLECTION,
                filter={"deployStatus": "green", "agent": category}
            )
        ]
        before_doc, current_doc = await asyncio.gather(*tasks_1)
        before_document_id = before_doc["_id"]
        current_document_id = current_doc["_id"]

        # 2. update date and status
        tasks_2 = [
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": current_document_id},
                update={"$set": {"deployStatus": "blue"}}
            ),
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": before_document_id},
                update={"$set": {"deployStatus": "green", "date": deploy_date}}
            )
        ]
        await asyncio.gather(*tasks_2)

    except DBError as e:
        logging.error(f"[helper.operation.helper_rollback_not_aireport] DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.operation.helper_rollback_not_aireport] Exception: {e}")
        raise Exception(e)


async def helper_get_current_model(main_db_client: MongoClient, category:str):
    try:
        document = await main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={"agent": category}
        )

        if document and document.get('vendor') and document.get('model'):
            result = {
                'company': document['vendor'],
                'model': document['model']
            }
        else:
            result = {
                'company': None,
                'model': None
            }

        return result

    except DBError as e:
        logging.error(f"[helper.operation.helper_get_current_model] DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.operation.helper_get_current_model] Exception: {e}")
        raise Exception(e)


async def helper_set_vendor_and_model(
    main_db_client: MongoClient,
    payload: SetVendorAndModelPayload
):
    try:
        # 0. deploy date
        deploy_date = datetime.now(timezone.utc)

        # 1. get for judge insert or update
        current_model_document = await main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={"agent": payload.agent}
        )

        # 2. update or insert
        if current_model_document and current_model_document.get('_id'):
            await main_db_client.update_one(
                collection=MODEL_COLLECTION,
                filter={"_id": current_model_document['_id']},
                update={"$set": {"vendor": payload.vendor, "model": payload.model, "date": deploy_date}},
            )
        else:
            await main_db_client.insert_one(
                collection=MODEL_COLLECTION,
                document={
                    "vendor": payload.vendor,
                    "model": payload.model,
                    "date": deploy_date,
                    "agent": payload.agent
                }

            )

    except DBError as e:
        logging.error(f"[helper.operation.helper_set_current_model] DBError: {e.message}]")
        raise DBError(e.message)
    except Exception as e:
        logging.error(f"[helper.operation.helper_set_current_model] Exception: {e}")
        raise Exception(e)


def reform_result_id_cursor(cursor:list, category:str):
    """
    MongoClient().find에서 얻은 cursor 데이터를 Parsing하는 함수\n\n
    args:\n
        cursors: Mongo에서 조회 얻은 결과 object\n
        category: 프론트 페이지 pathname. ex) cs, contactUs, aireport
    """
    result = list()
    for c in cursor:
        data = {
            "id":str(c['_id']),
            "date": c.get('date'),
        }
        result.append(data)
    return result


def reform_version_refer_cursor(cursor):
    # refer_list = [c['rid'] for c in cursor if c.get('rid', False)]
    refer_list = list()
    for c in cursor:
        refer_list += c.get('rid', '')
    refer_set = set(refer_list)
    result = [
        {
            "id": rid,
            "date": rid,
            "getResult": True #무조건 결과가 있음. cursor에 있는 데이터가 질문과 답변 이벤트를 기록한 데이터이기 때문
        } for rid in refer_set
    ]
    return result

def reform_version_cursor(cursor, kind:str, category:str):
    getResult = True if kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST else False
    result_dict = dict()
    tid_check_set = set()
    is_indepth_check_list = list()
    for c in cursor:
        prompt_data = {
            "id":str(c['_id']),
            "date": c['date'],
            "memo": c.get('memo', None),
            "getResult": True if getResult else c.get('getResult', False),
        }
        order = c.get("order", None)
        tid = c.get("tid", "previous") # True if cursor is result of conversationResult
        if tid not in tid_check_set and order:
            tid_check_set.add(tid)
            prompt_data["order"] = c["order"]
            result_dict[tid] = [prompt_data]
            is_indepth_check_list.append(True)
        elif tid in tid_check_set and order:
            prompt_data["order"] = c["order"]
            result_dict[tid].append(prompt_data)
            is_indepth_check_list.append(True)
        elif tid in tid_check_set and not order:
            prompt_data["order"] = 1
            result_dict[tid].append(prompt_data)
            is_indepth_check_list.append(False)
        else:
            tid_check_set.add(tid)
            prompt_data["order"] = 1
            result_dict[tid] = [prompt_data]
            is_indepth_check_list.append(False)

    is_indepth = any(is_indepth_check_list)
    if is_indepth:
        result = [{'groupId': key, 'versions': sorted(value, key=lambda x: x['order'])} for key, value in result_dict.items()]
    else:
        result = result_dict['previous']

    return result


def reform_version_module_cursor(cursor):
    result_dict = dict()
    check_set = set()
    for c in cursor:
        prompt_data = {
            "id":str(c['_id']),
            "date": c['date'],
            "memo": c.get('memo', None),
            "getResult": c.get('getResult', False),
        }
        roleName = c.get("roleName", "previous") # True if cursor is result of prompt
        if roleName not in check_set and roleName:
            check_set.add(roleName)
            result_dict[roleName] = [prompt_data]
        elif roleName in check_set and roleName:
            result_dict[roleName].append(prompt_data)
        else:
            pass
    # list로 담아주기 위해 한번 더 transform
    result = [{'groupId': key, 'versions': sorted(value, key=lambda x: x['date'])} for key, value in result_dict.items()]
    # sorted(data, key=lambda x: x['value'], reverse=True)
    return result


async def reform_chat_cursor(main_db_client:MongoClient, cursor:object, category:str= None, kind:str=None):
    try:
        result = {
            "id": str(cursor['_id']),
            "message" if kind != filter else "prompt": cursor['message'],
            "date": cursor['date'],
        }

        memo = cursor.get('memo', None)

        if memo:
            result["memo"] = memo

        if kind == RESULT:
            rid = cursor.get('rid', None)
            if rid:
                result["refer"] = {"id":rid}
            pid = cursor.get('pid', None)
            if pid:
                pingpong = type(pid[0]) == list
                if pingpong:
                    pids = [pid for sublist in pid for pid in sublist]
                    result["prompt"] = []
                    for enum, pid in enumerate(pids):
                        prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(pid)})
                        result["prompt"].append({"id":pid, "date": prompt_data['date'], "order": enum+1, "roleName": prompt_data['roleName']})
                else:
                    if type(pid) == list:
                        result["prompt"] = []
                        for enum, pid_each in enumerate(pid):
                            prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(pid_each)})
                            result["prompt"].append({"id":pid, "date": prompt_data['date'], "order": enum+1, "roleName": prompt_data['roleName']})
                    else:
                        prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(pid)})
                        result["prompt"] = {"id":pid, "date": prompt_data['date']}

            qid = cursor.get('qid', None)
            if qid:
                query_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(qid)})
                result["query"] = {"id": qid, "date": query_data['date']}

            cid = cursor.get('cid', None)
            if cid: #TODO@jaehoon: should make CLEAN CODE!
                filename_data = cursor.get('filename', None)
                if filename_data:
                    filename, filename_list = make_filename(filename_data)
                    result["chat"] = {"id":cid, "filename": filename}
                    if filename_list:
                        result["chat"]["filename_list"] = filename_list
                else: #파일을 넣지 않았을 경우를 대비한 예외처리
                    result["chat"] = {"id":cid, "filename": "question.txt"}
                chat_data = await main_db_client.find_one(collection=CHAT_COLLECTION, filter={"_id": ObjectId(cid)})
                result["chat"]["date"] = chat_data['date']

            tid = cursor.get('tid', None)
            if tid:
                result["tail"] = {"id": tid}

        return result

    except DBError as e:
        logging.info(f"[helper.operation.reform_chat_cursor] 🔴 Failed to reform chat cursor: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.operation.reform_chat_cursor] 🔴 Failed to reform chat cursor: {e}")
        raise Exception(e)


def reform_chat_pingpong_cursor(cursor:object):
    try:
        result_dict = dict()
        check_list = list()
        for c in cursor:
            tid = c.get("tid", None)
            filename_data = c.get('filename', None)
            if filename_data:
                filename, filename_list = make_filename(filename_data)
            else:
                filename = "question.txt"
                filename_list = None
            prompt_data = {
                "id": str(c['_id']),
                "message": c['message'],
                "date": c['date'],
                "chat": {"id": c.get('cid', None), "filename": filename, "filename_list": filename_list},
                "prompt": {"id": c.get('pid', None)},
                "refer": {"id": c.get('rid', None)},
            }
            qid = c.get('qid', None)
            if qid:
                prompt_data['filter'] = {"id":qid}
            if tid not in check_list and tid:
                    check_list.append(tid)
                    result_dict[tid] = [prompt_data]
            elif tid in check_list and tid:
                result_dict[tid].append(prompt_data)
            else:
                pass
        # list로 담아주기 위해 한번 더 transform
        result = [{key:value} for key, value in result_dict.items()]
        return result

    except Exception as e:
        logging.info(f"[helper.operation.reform_chat_pingpong_cursor] 🔴 Failed to reform chat pingpong cursor: {e}")
        raise Exception(e)


def reform_prompt_cursor(cursor:dict):
    # if not tid:
    try:
        result = {
            "id": str(cursor['_id']),
            "prompt":cursor['prompt'],
            "memo": cursor['memo'],
            "date": cursor['date'],
        }
        if cursor.get('roleName', None):
            result["roleName"] = cursor['roleName']
        if cursor.get('order', None):
            result["order"] = cursor['order']
        return result

    except Exception as e:
        logging.info(f"[helper.operation.reform_prompt_cursor] 🔴 Failed to reform prompt cursor: {e}")
        raise Exception(e)


def reform_prompt_pingpong_cursor(cursor:object):
    try:
        result_dict = dict()
        check_list = list()
        for c in cursor:
            tid = c.get("tid", None)
            prompt_data = {
                "id": str(c['_id']),
                "prompt":c['prompt'],
                "memo": c['memo'],
                "date": c['date'],
                "order": c['order'],
                "tail_id": c['tid']
            }
            if tid not in check_list and tid:
                    check_list.append(tid)
                    result_dict[tid] = [prompt_data]
            elif tid in check_list and tid:
                result_dict[tid].append(prompt_data)
            else:
                pass
        # list로 담아주기 위해 한번 더 transform
        result = [{key:value} for key, value in result_dict.items()]
        return result

    except Exception as e:
        logging.info(f"[helper.operation.reform_prompt_pingpong_cursor] 🔴 Failed to reform prompt pingpong cursor: {e}")
        raise Exception(e)


def reform_refer_response(response:object):
    try:
        result = dict()
        for id, data in response.vectors.items():
            result["id"] = id
            result["prompt"] = data.metadata['text']
            result["memo"] = data.metadata.get('memo', None)
            result["date"] = data.metadata.get('updatedAt', None)
        return result

    except Exception as e:
        logging.info(f"[helper.operation.reform_refer_response] 🔴 Failed to reform refer response: {e}")
        raise Exception(e)


def get_id(category:str, kind:str):
    """
    Set Filter Key For getting Result
    """
    try:
        if kind == PROMPT:
            key = 'pid'
        elif kind == QUERY and category in QUERY_CATEGORY_PROMPT_LIST:
            key = 'qid'
        elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
            key = 'cid'
        elif kind == REFER:
            key = 'rid'
        else:
            raise KeyError("Invalid Data")
        return key

    except KeyError as e:
        logging.info(f"[helper.operation.get_id] 🔴 Failed to get id: {e}")
        raise Exception(e)
    except Exception as e:
        logging.info(f"[helper.operation.get_id] 🔴 Failed to get id: {e}")
        raise Exception(e)


def get_collection(category:str, kind:str):
    try:
        if kind == RESULT:
            collection = CHAT_COLLECTION
        elif kind == PROMPT:
            collection = PROMPT_COLLECTION
        elif kind == QUERY and category in QUERY_CATEGORY_PROMPT_LIST:
            collection = PROMPT_COLLECTION
        elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
            collection = CHAT_COLLECTION
        elif kind == REFER:
            collection = CHAT_COLLECTION
        else:
            raise KeyError()
        return collection

    except KeyError as e:
        logging.info(f"[helper.operation.get_collection] 🔴 Failed to get collection: {e}")
        raise Exception(e)
    except Exception as e:
        logging.info(f"[helper.operation.get_collection] 🔴 Failed to get collection: {e}")
        raise Exception(e)


def get_module(category:str):
    mode = False
    return mode


def get_namespace(id:str):
    if "book" in id:
        namespace = "book"
    elif "swcag2023" in id:
        namespace = "swcag2023"
    else:
        namespace = "forum"
    return namespace


def make_version_filter(category:str, kind:str, roleName:str):
    """
    Make filter filter for Mongo collection
    """
    try:
        if kind == RESULT:
            filter = {'agent':category, 'role':'ai'}
        elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
            filter = {'agent':category, 'role':'human'}
        elif kind in PROM_KIND_HISTORY_LIST:
            filter = {'agent':category, 'kind':kind}
        else:
            filter = {'agent':category, 'role':'ai'}

        if roleName:
            filter['roleName'] = roleName


        return filter

    except Exception as e:
        logging.info(f"[helper.operation.make_version_filter] 🔴 Failed to make version filter: {e}")
        raise Exception(e)


def make_fileinfo(question_data, filename_data):
    try:
        if filename_data:
            filename, filename_list = make_filename(filename_data)
            data = json.loads(question_data)
            # 1개의 데이터만 업로드한 경우
            if not filename_list:
                filedata = io.BytesIO()
                filedata.write(json.dumps(data,ensure_ascii=False).encode('utf-8'))
                filedata.seek(0)
                mimetype = 'application/json; charset=utf-8'
            # 2개 이상 데이터 업로드한 경우
            else:
                filedata = io.BytesIO()
                with zipfile.ZipFile(filedata, 'w') as zipf:
                    for n, d in zip(filename_list, data):
                        zipf.writestr(f"{n}.json", json.dumps(d, ensure_ascii=False))
                filedata.seek(0)
                mimetype = 'application/zip; charset=utf-8'
        else:
            filename = "question.txt"
            filedata = str(question_data)
            mimetype = 'text/plain; charset=utf-8'
        filename = filename.encode('utf-8').decode('latin-1')
        return filename, filedata, mimetype

    except Exception as e:
        logging.info(f"[helper.operation.make_fileinfo] 🔴 Failed to make fileinfo: {e}")
        raise Exception(e)


def make_filename(filename_data):
    try:
        if not filename_data:
            filename = None
            filename_list = None
        else:
            if filename_data[0] == "[" and filename_data[-1] == "]":
                filename_list = [name.split(".")[0] for name in ast.literal_eval(filename_data)]
                filename = "-".join(filename_list) + ".zip"
                filename = filename.replace(' ', '')
            else:
                filename = filename_data
                filename_list = None
        return filename, filename_list

    except Exception as e:
        logging.info(f"[helper.operation.make_filename] 🔴 Failed to make filename: {e}")
        raise Exception(e)
