import io
import os
import ast
import json
import asyncio
import logging
import zipfile
from datetime import datetime, timezone
from bson import ObjectId

from fastapi.responses import StreamingResponse

from payload.agent import *
from utils.constants import *
from utils.error import DBError, VectorDBError

from client.mongo import MongoClient, ProductionMongoClient
from client.pinecone import PineconeClient


# ==================== Prompt ====================

async def helper_insert_prompt_data(main_db_client:MongoClient, payload:InsertPromptPayload):
    try:
        data = {
            "prompt": payload.prompt,
            "memo": payload.memo,
            "agent": payload.agent,
            "date": datetime.now(timezone.utc),
            "getResult": False,
        }
        await main_db_client.insert_one(collection=PROMPT_COLLECTION, document=data)
    except DBError as e:
        logging.info(f"[helper.agent.helper_insert_prompt_data] 🔴 Failed to insert prompt data: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_insert_prompt_data] 🔴 Failed to insert prompt data: {e}")
        raise Exception(e)


async def helper_get_version(main_db_client:MongoClient, payload):
    try:
        category = payload.agent
        kind = payload.kind
        role_name = getattr(payload, 'role_name', None)

        collection = _get_collection(category, kind)
        filter = _make_version_filter(category=category, kind=kind, roleName=role_name)
        sort = [("date", -1)]
        cursor = await main_db_client.find(collection=collection, filter=filter, sort=sort)
        if kind == REFER:
            data = _reform_version_refer_cursor(cursor)
        else:
            data = _reform_version_cursor(cursor=cursor, category=category, kind=kind)
        return data
    except DBError as e:
        logging.info(f"[helper.agent.helper_get_version] 🔴 Failed to get version data: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_version] 🔴 Failed to get version data: {e}")
        raise Exception(e)


async def helper_get_prompt(main_db_client:MongoClient, payload):
    try:
        filter = {'_id': ObjectId(payload.id)}
        cursor = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter=filter)
        data = _reform_prompt_cursor(cursor=cursor)
        return data
    except DBError as e:
        logging.info(f"[helper.agent.helper_get_prompt] 🔴 Failed to get prompt: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_prompt] 🔴 Failed to get prompt: {e}")
        raise Exception(e)


async def helper_get_prompt_versions(main_db_client: MongoClient, payload: GetPromptVersionsPayload):
    try:
        sort = [("date", -1)]
        filter = {'agent': payload.agent}
        cursor = await main_db_client.find(collection=PROMPT_COLLECTION, filter=filter, sort=sort)
        result = [
            {
                "id": str(c['_id']),
                "date": c['date'],
                "memo": c.get('memo', None),
                "getResult": c.get('getResult', False),
            } for c in cursor
        ]
        logging.info(f"[helper.agent.helper_get_prompt_versions] result: {result}")
        return result
    except DBError as e:
        logging.info(f"[helper.agent.helper_get_prompt_versions] 🔴 Failed to get prompt versions: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_prompt_versions] 🔴 Failed to get prompt versions: {e}")
        raise Exception(e)


async def helper_get_prompt_data(main_db_client: MongoClient, payload: GetPromptDataPayload):
    try:
        _id = payload.id
        cursor = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(_id)})
        if not cursor:
            return None

        return _reform_prompt_cursor(cursor=cursor)

    except DBError as e:
        logging.info(f"[helper.agent.helper_get_prompt_data] 🔴 Failed to get prompt data: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_prompt_data] 🔴 Failed to get prompt data: {e}")
        raise Exception(e)


async def helper_get_data(main_db_client:MongoClient, vector_db_client:PineconeClient, payload):
    try:
        category = payload.agent
        id = payload.id
        kind = payload.kind
        page = payload.page
        if not id:
            id = "670bf833963d3e3d97870364"

        if kind != REFER:
            collection = _get_collection(category, kind)
            filter = {'_id': ObjectId(id)}
            cursor = await main_db_client.find_one(collection=collection, filter=filter)
            if collection == PROMPT_COLLECTION:
                data = _reform_prompt_cursor(cursor=cursor)
            elif collection == CHAT_COLLECTION:
                data = await _reform_chat_cursor(main_db_client=main_db_client, cursor=cursor, category=category, kind=kind)
        else:
            ids = [str(id)]
            response = await vector_db_client.fetch(ids=ids)
            data = _reform_refer_response(response)

        if kind != RESULT:
            key = _get_id(category=category, kind=kind)
            value = str(id) if kind not in [PROMPT, REFER] else {"$in": [str(id)]}
            filter = {key: value, "role": "ai"}
            sort = [("date", -1)]
            limit = 5 if page else None
            skip = (page - 1) * limit if page else None
            cursor = await main_db_client.find(collection=CHAT_COLLECTION, filter=filter, sort=sort, skip=skip, limit=limit)
            result_data = _reform_result_id_cursor(cursor=cursor, category=category)
            if not result_data:
                value = {"$elemMatch": {"$elemMatch": {"$eq": str(id)}}}
                filter = {key: value, "role": "ai"}
                cursor = await main_db_client.find(collection=CHAT_COLLECTION, filter=filter, sort=sort, skip=skip, limit=limit)
                result_data = _reform_result_id_cursor(cursor=cursor, category=category)
            data['result'] = result_data

        return data

    except DBError as e:
        logging.info(f"[helper.agent.helper_get_data] 🔴 Failed to get data: {e}")
        raise DBError(e)
    except VectorDBError as e:
        logging.info(f"[helper.agent.helper_get_data] 🔴 Failed to get data: {e}")
        raise VectorDBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_data] 🔴 Failed to get data: {e}")
        raise Exception(e)


async def helper_update_memo(main_db_client:MongoClient, payload):
    try:
        filter = {'_id': ObjectId(payload.id)}
        update = {"$set": {'memo': payload.memo}}
        collection = _get_collection(category=payload.agent, kind=payload.kind)
        await main_db_client.update_one(collection=collection, filter=filter, update=update)
    except DBError as e:
        logging.info(f"[helper.agent.helper_update_memo] 🔴 Failed to update memo: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_update_memo] 🔴 Failed to update memo: {e}")
        raise Exception(e)


async def helper_download_question(main_db_client:MongoClient, id:str):
    try:
        filter = {'_id': ObjectId(id)}
        cursor = await main_db_client.find_one(collection=CHAT_COLLECTION, filter=filter)
        question_data = cursor['message']
        filename_data = cursor.get('filename', None)
        filename, filedata, mimetype = _make_fileinfo(question_data, filename_data)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        if isinstance(filedata, io.BytesIO):
            return StreamingResponse(filedata, media_type=mimetype, headers=headers)
        elif isinstance(filedata, str):
            bytes_io = io.BytesIO(filedata.encode('utf-8'))
            return StreamingResponse(bytes_io, media_type=mimetype, headers=headers)
    except DBError as e:
        logging.info(f"[helper.agent.helper_download_question] 🔴 Failed to download question: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_download_question] 🔴 Failed to download question: {e}")
        raise Exception(e)


# ==================== Model ====================

async def helper_get_current_model(main_db_client:MongoClient, category:str):
    try:
        document = await main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={"agent": category}
        )
        if document and document.get('vendor') and document.get('model'):
            return {'company': document['vendor'], 'model': document['model']}
        return {'company': None, 'model': None}
    except DBError as e:
        logging.error(f"[helper.agent.helper_get_current_model] DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.error(f"[helper.agent.helper_get_current_model] Exception: {e}")
        raise Exception(e)


async def helper_set_vendor_and_model(main_db_client:MongoClient, payload):
    try:
        deploy_date = datetime.now(timezone.utc)
        current = await main_db_client.find_one(
            collection=MODEL_COLLECTION,
            filter={"agent": payload.agent}
        )
        if current and current.get('_id'):
            await main_db_client.update_one(
                collection=MODEL_COLLECTION,
                filter={"_id": current['_id']},
                update={"$set": {"vendor": payload.vendor, "model": payload.model, "date": deploy_date}},
            )
        else:
            await main_db_client.insert_one(
                collection=MODEL_COLLECTION,
                document={"vendor": payload.vendor, "model": payload.model, "date": deploy_date, "agent": payload.agent}
            )
    except DBError as e:
        logging.error(f"[helper.agent.helper_set_vendor_and_model] DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.error(f"[helper.agent.helper_set_vendor_and_model] Exception: {e}")
        raise Exception(e)


# ==================== Deploy ====================

async def helper_deploy_whole(production_main_db_client:ProductionMongoClient, staging_main_db_client:MongoClient, category:str):
    try:
        deploy_date = datetime.now(timezone.utc)
        staging_prompt_doc, current_production_prompt_doc = await asyncio.gather(
            staging_main_db_client.find_one(collection=PROMPT_COLLECTION, filter={'agent': category}, sort=[("date", -1)]),
            production_main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"agent": category}, sort=[("date", -1)])
        )
        current_production_prompt_doc_id = current_production_prompt_doc["_id"]
        staging_prompt_doc['date'] = deploy_date
        staging_prompt_doc['deployStatus'] = "green"
        await asyncio.gather(
            production_main_db_client.insert_one(collection=PROMPT_COLLECTION, document=staging_prompt_doc),
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": current_production_prompt_doc_id},
                update={"$set": {"deployStatus": "blue"}}
            )
        )
    except DBError as e:
        logging.error(f"[helper.agent.helper_deploy_whole] DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.error(f"[helper.agent.helper_deploy_whole] Exception: {e}")
        raise Exception(e)


async def helper_get_deploy_list(production_main_db_client:ProductionMongoClient, staging_main_db_client:MongoClient):
    try:
        sort = [("date", 1)]
        real_prompt_data = {
            doc['agent']: doc
            for doc in await production_main_db_client.find(collection=PROMPT_COLLECTION, filter={"deployStatus": "green"}, sort=sort)
        }
        staging_prompt_data = {
            doc['agent']: doc
            for doc in await staging_main_db_client.find(collection=PROMPT_COLLECTION, filter={}, sort=sort)
        }
        update_module_list = [
            category for category in staging_prompt_data
            if category not in real_prompt_data or staging_prompt_data[category]['date'] > real_prompt_data[category].get('date', datetime.min)
        ]
        return {"update_type_list": [], "update_module_list": update_module_list}
    except DBError as e:
        logging.info(f"[helper.agent.helper_get_deploy_list] 🔴 Failed to get deploy list: {e}")
        raise DBError(e)
    except Exception as e:
        logging.info(f"[helper.agent.helper_get_deploy_list] 🔴 Failed to get deploy list: {e}")
        raise Exception(e)


async def helper_rollback_not_aireport(production_main_db_client:ProductionMongoClient, category:str):
    try:
        deploy_date = datetime.now(timezone.utc)
        before_doc, current_doc = await asyncio.gather(
            production_main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"deployStatus": "blue", "agent": category}),
            production_main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"deployStatus": "green", "agent": category})
        )
        await asyncio.gather(
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": current_doc["_id"]},
                update={"$set": {"deployStatus": "blue"}}
            ),
            production_main_db_client.update_one(
                collection=PROMPT_COLLECTION,
                filter={"_id": before_doc["_id"]},
                update={"$set": {"deployStatus": "green", "date": deploy_date}}
            )
        )
    except DBError as e:
        logging.error(f"[helper.agent.helper_rollback_not_aireport] DBError: {e}")
        raise DBError(e)
    except Exception as e:
        logging.error(f"[helper.agent.helper_rollback_not_aireport] Exception: {e}")
        raise Exception(e)


# ==================== Vector Index ====================

def get_vector_db_index(category:str, server_stage:str) -> str:
    if category in UXGPT_LIST:
        return CONTACTUS_INDEX if server_stage == PRODUCTION else CONTACTUS_STAGING_INDEX
    elif category == "reportchat":
        return REPORTCHAT_INDEX
    return MAIN_INDEX


# ==================== Private Utils ====================

def _get_collection(category:str, kind:str):
    if kind == RESULT:
        return CHAT_COLLECTION
    elif kind == PROMPT:
        return PROMPT_COLLECTION
    elif kind == QUERY and category in QUERY_CATEGORY_PROMPT_LIST:
        return PROMPT_COLLECTION
    elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
        return CHAT_COLLECTION
    elif kind == REFER:
        return CHAT_COLLECTION
    raise KeyError(f"Invalid kind: {kind}")


def _get_id(category:str, kind:str):
    if kind == PROMPT:
        return 'pid'
    elif kind == QUERY and category in QUERY_CATEGORY_PROMPT_LIST:
        return 'qid'
    elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
        return 'cid'
    elif kind == REFER:
        return 'rid'
    raise KeyError("Invalid Data")


def _make_version_filter(category:str, kind:str, roleName:str=None):
    if kind == RESULT:
        filter = {'agent': category, 'role': 'ai'}
    elif kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST:
        filter = {'agent': category, 'role': 'human'}
    elif kind in PROM_KIND_HISTORY_LIST:
        filter = {'agent': category, 'kind': kind}
    else:
        filter = {'agent': category, 'role': 'ai'}
    if roleName:
        filter['roleName'] = roleName
    return filter


def _reform_result_id_cursor(cursor:list, category:str):
    return [{"id": str(c['_id']), "date": c.get('date')} for c in cursor]


def _reform_version_refer_cursor(cursor):
    refer_list = []
    for c in cursor:
        refer_list += c.get('rid', '')
    return [{"id": rid, "date": rid, "getResult": True} for rid in set(refer_list)]


def _reform_version_cursor(cursor, kind:str, category:str):
    getResult = True if kind == QUERY and category not in QUERY_CATEGORY_PROMPT_LIST else False
    result_dict = dict()
    tid_check_set = set()
    is_indepth_check_list = []
    for c in cursor:
        prompt_data = {
            "id": str(c['_id']),
            "date": c['date'],
            "memo": c.get('memo', None),
            "getResult": True if getResult else c.get('getResult', False),
        }
        order = c.get("order", None)
        tid = c.get("tid", "previous")
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

    if any(is_indepth_check_list):
        return [{'groupId': key, 'versions': sorted(value, key=lambda x: x['order'])} for key, value in result_dict.items()]
    return result_dict.get('previous', [])


def _reform_prompt_cursor(cursor:dict):
    result = {
        "id": str(cursor['_id']),
        "prompt": cursor['prompt'],
        "memo": cursor['memo'],
        "date": cursor['date'],
    }
    if cursor.get('roleName'):
        result["roleName"] = cursor['roleName']
    if cursor.get('order'):
        result["order"] = cursor['order']
    return result


def _reform_refer_response(response:object):
    result = {}
    for id, data in response.vectors.items():
        result["id"] = id
        result["prompt"] = data.metadata['text']
        result["memo"] = data.metadata.get('memo', None)
        result["date"] = data.metadata.get('updatedAt', None)
    return result


async def _reform_chat_cursor(main_db_client:MongoClient, cursor:object, category:str=None, kind:str=None):
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
            result["refer"] = {"id": rid}
        pid = cursor.get('pid', None)
        if pid:
            pingpong = type(pid[0]) == list
            if pingpong:
                pids = [p for sublist in pid for p in sublist]
                result["prompt"] = []
                for enum, p in enumerate(pids):
                    prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(p)})
                    result["prompt"].append({"id": p, "date": prompt_data['date'], "order": enum+1, "roleName": prompt_data['roleName']})
            else:
                if type(pid) == list:
                    result["prompt"] = []
                    for enum, pid_each in enumerate(pid):
                        prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(pid_each)})
                        result["prompt"].append({"id": pid, "date": prompt_data['date'], "order": enum+1, "roleName": prompt_data['roleName']})
                else:
                    prompt_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(pid)})
                    result["prompt"] = {"id": pid, "date": prompt_data['date']}

        qid = cursor.get('qid', None)
        if qid:
            query_data = await main_db_client.find_one(collection=PROMPT_COLLECTION, filter={"_id": ObjectId(qid)})
            result["query"] = {"id": qid, "date": query_data['date']}

        cid = cursor.get('cid', None)
        if cid:
            filename_data = cursor.get('filename', None)
            if filename_data:
                filename, filename_list = _make_filename(filename_data)
                result["chat"] = {"id": cid, "filename": filename}
                if filename_list:
                    result["chat"]["filename_list"] = filename_list
            else:
                result["chat"] = {"id": cid, "filename": "question.txt"}
            chat_data = await main_db_client.find_one(collection=CHAT_COLLECTION, filter={"_id": ObjectId(cid)})
            result["chat"]["date"] = chat_data['date']

        tid = cursor.get('tid', None)
        if tid:
            result["tail"] = {"id": tid}

    return result


def _make_fileinfo(question_data, filename_data):
    if filename_data:
        filename, filename_list = _make_filename(filename_data)
        data = json.loads(question_data)
        if not filename_list:
            filedata = io.BytesIO()
            filedata.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            filedata.seek(0)
            mimetype = 'application/json; charset=utf-8'
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


def _make_filename(filename_data):
    if not filename_data:
        return None, None
    if filename_data[0] == "[" and filename_data[-1] == "]":
        filename_list = [name.split(".")[0] for name in ast.literal_eval(filename_data)]
        filename = "-".join(filename_list).replace(' ', '') + ".zip"
        return filename, filename_list
    return filename_data, None
