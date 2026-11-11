"""Agent domain router: server (split from api/agent.py — paths/signatures unchanged)."""
from fastapi import APIRouter, Depends
import json
from bson import ObjectId
from payload.agent import *
from helper.agent import *
from utils.error import *
from response import Res200, Res400
from client.mongo import MongoClient
from client.redis import RedisClient
from client.fastmcp import FastMCPClient
from client import get_main_db, get_memory_db


agent = APIRouter(prefix="/agent", tags=["Agent"])


@agent.post("/enroll_mcp_server", response_model=Res200)
@handle_errors()
async def enroll_mcp_server(
    payload: EnrollMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    document = {
        'name': payload.name,
        'uri': payload.uri,
        'token': payload.token,
        'desc': payload.description,
    }
    await main_db_client.insert_one(collection=MCP_SERVER_COLLECTION, document=document)

    # make response and return
    return Res200()


@agent.get("/get_mcp_server", response_model=Res200)
@handle_errors()
async def get_mcp_server(
    main_db_client: MongoClient = Depends(get_main_db),
    memory_db_client: RedisClient = Depends(get_memory_db),
):
    # business logic
    documents = await main_db_client.find(collection=MCP_SERVER_COLLECTION, filter={})

    result = []
    for document in documents:
        server_id = str(document['_id'])

        server_info = {
            'id': server_id,
            'name': document['name'],
            'uri': document['uri'],
            'description': document.get('desc', ''),
        }
        logging.info(f"[agent.get_mcp_server] server_info: {server_info}")
        logging.info(f"[agent.get_mcp_server] document: {document}")

        # check Redis cache first
        cache_key = f"mcp_health:{server_id}"
        cached = await memory_db_client.get(cache_key)

        if cached:
            tools = json.loads(cached)
            server_info['live'] = True
            server_info['tools'] = tools
        else:
            tools = await FastMCPClient(document["uri"], document["token"]).list_tools()
            if tools:
                server_info['live'] = True
                server_info['tools'] = [{'toolName': tool['name'], 'description': tool['description']} for tool in tools]
                # cache in Redis with 30s TTL
                await memory_db_client.set_with_expire(cache_key, json.dumps(server_info['tools']), 30)
            else:
                server_info['live'] = False
                server_info['tools'] = []

        result.append(server_info)

    return Res200(data=result)


@agent.post("/update_mcp_server", response_model=Res200)
@handle_errors()
async def update_mcp_server(
    payload: UpdateMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    _filter = {"_id": ObjectId(payload.id)}
    update = {"$set": {}}
    if payload.name:
        update["$set"]["name"] = payload.name
    if payload.uri:
        update["$set"]["uri"] = payload.uri
    if payload.description:
        update["$set"]["desc"] = payload.description
    await main_db_client.update_one(collection=MCP_SERVER_COLLECTION, filter=_filter, update=update)

    # make response and return
    return Res200()


@agent.post("/delete_mcp_server", response_model=Res200)
@handle_errors()
async def delete_mcp_server(
    payload: DeleteMCPServerPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # check if any toolsets reference this server
    referencing_toolsets = await main_db_client.find(
        collection=AGENT_COLLECTION,
        filter={"mcpInfo.serverId": payload.id}
    )
    if referencing_toolsets:
        affected_names = [toolset.get('name', 'unknown') for toolset in referencing_toolsets]
        return Res400(
            message=f"Cannot delete server. Referenced by toolsets: {', '.join(affected_names)}"
        ).to_response()

    # business logic
    delete_filter = {"_id": ObjectId(payload.id)}
    await main_db_client.delete_one(collection=MCP_SERVER_COLLECTION, filter=delete_filter)

    # make response and return
    return Res200()
