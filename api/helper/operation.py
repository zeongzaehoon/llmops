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


def get_vector_db_index(category:str, server_stage:str) -> str:
    if category in UXGPT_LIST:
        vector_db_index = CONTACTUS_INDEX if server_stage == PRODUCTION else CONTACTUS_STAGING_INDEX
    elif category == "reportchat":
        vector_db_index = REPORTCHAT_INDEX
    else:
        vector_db_index = MAIN_INDEX
    return vector_db_index


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
