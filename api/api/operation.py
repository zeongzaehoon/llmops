from fastapi import APIRouter, Depends
import tiktoken

from auth.dependencies import get_optional_user
from helper.operation import *
from utils.error import *
from utils.response import *
from client.mongo import MongoClient, ProductionMongoClient
from client.pinecone import PineconeClient
from client import get_main_db, get_production_db



operation = APIRouter(prefix="/operation", tags=["Operation"])



@operation.post("/get_version")
@handle_errors()
async def _get_version(
    payload: getVersionPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_version(main_db_client=main_db_client, payload=payload)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@operation.post("/get_data")
@handle_errors()
async def _get_data(
    payload: getDataPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # server stage
    stage = os.getenv("SERVER_STAGE", "development")

    # client
    vector_db_index_name = get_vector_db_index(category=payload.agent, server_stage=stage)
    vector_db_client = PineconeClient(index_name=vector_db_index_name)

    # business logic
    data = await helper_get_data(main_db_client=main_db_client, vector_db_client=vector_db_client, payload=payload)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@operation.post("/download_question")
@handle_errors()
async def _download_question(
    payload: downloadQuestionPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # payload
    id = payload.id

    # get request data from main_db
    response = await helper_download_question(main_db_client=main_db_client, id=id)

    # return response
    return response


@operation.post("/update_memo")
@handle_errors()
async def _update_memo(
    payload: updateMemoPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # update memo to main_db
    await helper_update_memo(main_db_client=main_db_client, payload=payload)

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@operation.post("/get_token_size")
@handle_errors()
async def _get_token_size(
    payload: getTokenSize
):
    content = payload.prompt
    if not content:
        return Response500(message="THERE ARE NOT CONTENT").to_dict()
    encoding = tiktoken.get_encoding(BASE_MODEL)
    tokens = encoding.encode(content)
    return len(tokens)



# for EAGLE
@operation.post("/update_not_satisfy")
@handle_errors()
async def _update_not_satisfy(
    payload: updateNotSatisfyPayload,
    session_key: str = Depends(get_optional_user),
    main_db_client: MongoClient = Depends(get_main_db),
):
    logging.info(f"payload.email: {payload.email}")
    logging.info(f"session_key: {session_key}")

    # get token info & payload
    email = payload.email

    # update data
    await main_db_client.update_many(
        collection=CHAT_COLLECTION,
        filter={'sessionKey': session_key},
        update={'$set': {'email': email, 'solved': False}}
    )

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()



@operation.post("/deploy")
@handle_errors()
async def _deploy(
    payload: deployPayload,
    staging_main_db_client: MongoClient = Depends(get_main_db),
    real_main_db_client: ProductionMongoClient = Depends(get_production_db),
):

    # payload & check stage, password
    logging.info("start to deploy prompt from staging to production")
    stage = payload.stage
    isStaging = stage == STAGING
    if not isStaging:
        logging.info("not isStaging")
        raise ForbiddenError()

    password = payload.password
    isPassword = password == PASSWORD
    if not isPassword:
        logging.info("not isPassword")
        raise ForbiddenError()

    # deploy prompt
    await helper_deploy_whole(
        production_main_db_client=real_main_db_client,
        staging_main_db_client=staging_main_db_client,
        category=payload.agent
    )

    # make response and return response
    return Response200(
        message="success"
    ).to_dict()


@operation.get("/get_deploy_list")
@handle_errors()
async def _get_deploy_list(
    staging_main_db_client: MongoClient = Depends(get_main_db),
    production_main_db_client: ProductionMongoClient = Depends(get_production_db),
):
    # get deploy list from production & staging
    data = await helper_get_deploy_list(production_main_db_client=production_main_db_client, staging_main_db_client=staging_main_db_client)

    # make response
    return Response200(
        message="success",
        data=data
    ).to_dict()


@operation.post("/rollback")
@handle_errors()
async def _rollback(
    payload: rollbackPayload,
    production_main_db_client: ProductionMongoClient = Depends(get_production_db),
):

    # business logic
    isStaging = payload.stage == STAGING
    server_stage = os.getenv("SERVER_STAGE", "development")
    isServerStaging = server_stage == STAGING
    if isStaging and isServerStaging:
        password = payload.password
        isPassword = password == PASSWORD
        if not isPassword:
            raise ForbiddenError("cannot rollback because Wrong Password")

        await helper_rollback_not_aireport(
            production_main_db_client=production_main_db_client,
            category=payload.agent
        )

    else:
        raise ForbiddenError("cannot rollback because Invalid request")

    # make response
    return Response200(message="success").to_dict()


@operation.get("/get_models")
def _get_models(
    query_params:GetModelQueryParams=Depends(),
):
    data = {
        "modelList": MCP_MODEL_LIST if query_params.agent in MCP_LIST else MODEL_LIST
    }
    return Response200(
        message="success",
        data=data
    ).to_dict()


@operation.get("/get_current_model")
@handle_errors()
async def _get_current_model(
    query_params: GetCurrentModelQueryParams = Depends(),
    main_db_client: MongoClient = Depends(get_main_db),
):
    # query_params
    category = query_params.agent

    # get vendor and model
    data = await helper_get_current_model(main_db_client, category)

    # make response and return
    return Response200(data=data).to_dict()


@operation.post("/set_vendor_and_model")
@handle_errors()
async def _set_vendor_and_model(
    payload: SetVendorAndModelPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # insert & update
    await helper_set_vendor_and_model(main_db_client=main_db_client, payload=payload)

    # make response and return
    return Response200(message="success").to_dict()
