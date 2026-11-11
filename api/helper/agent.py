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


# ==================== Vector Index ====================

def get_vector_db_index(category:str, server_stage:str) -> str:
    if category in UXGPT_LIST:
        return CONTACTUS_INDEX if server_stage == PRODUCTION else CONTACTUS_STAGING_INDEX
    elif category == "reportchat":
        return REPORTCHAT_INDEX
    return MAIN_INDEX


# ==================== Private Utils ====================


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
