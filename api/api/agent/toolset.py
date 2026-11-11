"""Agent domain router: toolset (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
import pytz
from bson import ObjectId
from payload.agent import *
from helper.agent import *
from utils.error import *
from response import Res200, Res400
from client.mongo import MongoClient
from client import get_main_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


@agent.post("/create_mcp_toolset", response_model=Res200)
@handle_errors()
async def create_mcp_toolset(
    payload: CreateMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = {
        'agent': payload.agent,
        'name': payload.name,
        'regDate': pytz.timezone('Asia/Seoul').localize(datetime.now()),
        'mcpInfo': payload.mcp_info,
        'isService': False
    }
    if payload.description:
        document['desc'] = payload.description

    await main_db_client.insert_one(collection=MCP_TOOLSET_COLLECTION, document=document)

    # make response and return
    return Res200()


@agent.post("/get_mcp_toolset", response_model=Res200)
@handle_errors()
async def get_mcp_toolset(
    payload: GetMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    _filter = {'agent': payload.agent} if payload.agent else {}
    documents = await main_db_client.find(
        collection=MCP_TOOLSET_COLLECTION,
        filter=_filter,
        sort=[('regDate', -1)]
    )
    result = []
    if not documents:
        return Res200(data=result)
    mcp_server_ids = [_id['serverId'] for document in documents for _id in document['mcpInfo']]
    server_name_documents = await main_db_client.find(collection=MCP_SERVER_COLLECTION, filter={'_id': {'$in': mcp_server_ids}})
    server_names = {str(document['_id']): document['name'] for document in server_name_documents}

    # make response and return
    for document in documents:
        if document.get("mcpInfo"):
            for mcp_info in document["mcpInfo"]:
                if mcp_info.get('serverId') and mcp_info['serverId'] in server_names:
                    mcp_info['serverName'] = server_names[mcp_info['serverId']]
        document['id'] = str(document['_id'])
        document.pop('_id', None)
        document['description'] = document.get('desc', '')
        document.pop('desc', None)
        result.append(document)
    return Res200(data=result)


@agent.post("/update_mcp_toolset", response_model=Res200)
@handle_errors()
async def update_mcp_agent(
    payload: UpdateMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    mcp_info = [{'serverId': info['serverId'], 'tools': info['tools']} for info in payload.mcp_info] if payload.mcp_info else None # 프론트에 내려준 serverName은 mcpInfo에 담지 않기
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {"mcpInfo": mcp_info}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.description:
        update["$set"]["desc"] = payload.description
    await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=_filter, update=update)

    # make response and return
    return Res200()


@agent.post("/adapt_toolset_on_service", response_model=Res200)
@handle_errors()
async def adapt_agent_on_service(
    payload: AdaptToolsetOnServicePayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # verify target toolset exists
    target = await main_db_client.find_one(collection=MCP_TOOLSET_COLLECTION, filter={"_id": ObjectId(payload.id)})
    if not target:
        return Res400(message="Target toolset not found").to_response()

    # step 1: deactivate current active toolset
    false_filter = {"agent": payload.agent, "isService": True}
    false_update = {"$set": {"isService": False}}
    await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=false_filter, update=false_update)

    # step 2: activate target toolset, with compensating rollback on failure
    try:
        _filter = {"_id": ObjectId(payload.id)}
        update = {"$set": {"isService": True}}
        await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=_filter, update=update)
    except Exception:
        # rollback: re-activate the previously active toolset
        rollback_update = {"$set": {"isService": True}}
        await main_db_client.update_one(collection=MCP_TOOLSET_COLLECTION, filter=false_filter, update=rollback_update)
        raise

    # make response and return
    return Res200()


@agent.post("/delete_mcp_toolset", response_model=Res200)
@handle_errors()
async def delete_mcp_toolset(
    payload: DeleteMCPToolsetPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MCP_TOOLSET_COLLECTION, filter=delete_filter)

    # make response and return
    return Res200()
