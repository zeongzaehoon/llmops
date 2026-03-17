import tiktoken
from fastapi import APIRouter, Depends

from auth.dependencies import get_optional_user
from helper.operation import *
from utils.error import *
from response import Res200, Res500
from client.mongo import MongoClient, ProductionMongoClient
from client.pinecone import PineconeClient
from client import get_main_db, get_production_db



operation = APIRouter(prefix="/operation", tags=["Operation"])



@operation.post("/get_version", response_model=Res200)
@handle_errors()
async def _get_version(
    payload: getVersionPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # business logic
    data = await helper_get_version(main_db_client=main_db_client, payload=payload)

    # make response
    return Res200(
        message="success",
        data=data
    )


@operation.post("/get_data", response_model=Res200)
@handle_errors()
async def _get_data(
    payload: getDataPayload,
    main_db_client: MongoClient = Depends(get_main_db)
):
    # server stage
    stage = os.getenv("SERVER_STAGE", "development")

    # client
    vector_db_index_name = get_vector_db_index(category=payload.agent, server_stage=stage)
    vector_db_client = PineconeClient(index_name=vector_db_index_name)

    # business logic
    data = await helper_get_data(main_db_client=main_db_client, vector_db_client=vector_db_client, payload=payload)

    # make response
    return Res200(
        message="success",
        data=data
    )


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


@operation.post("/update_memo", response_model=Res200)
@handle_errors()
async def _update_memo(
    payload: updateMemoPayload,
    main_db_client: MongoClient = Depends(get_main_db),
):
    # update memo to main_db
    await helper_update_memo(main_db_client=main_db_client, payload=payload)

    # make response and return response
    return Res200(message="success")


@operation.post("/get_token_size")
@handle_errors()
async def _get_token_size(
    payload: getTokenSize
):
    content = payload.prompt
    if not content:
        return Res500(message="THERE ARE NOT CONTENT").to_response()
    model_name = payload.model or TIKTOKEN_MODEL_LIST[0]
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # fallback for older tiktoken versions that don't recognize newer model names
        fallback_encoding = "o200k_base" if model_name.startswith(("gpt-4o", "o1", "o3", "o4")) else "cl100k_base"
        encoding = tiktoken.get_encoding(fallback_encoding)
    tokens = encoding.encode(content)
    return len(tokens)



# for EAGLE
@operation.post("/update_not_satisfy", response_model=Res200)
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
    return Res200(message="success")



@operation.post("/deploy", response_model=Res200)
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
    return Res200(message="success")


@operation.get("/get_deploy_list", response_model=Res200)
@handle_errors()
async def _get_deploy_list(
    staging_main_db_client: MongoClient = Depends(get_main_db),
    production_main_db_client: ProductionMongoClient = Depends(get_production_db),
):
    if os.getenv("SERVER_STAGE", "development") != STAGING:
        return Res200(message="success", data=[])

    # get deploy list from production & staging
    data = await helper_get_deploy_list(production_main_db_client=production_main_db_client, staging_main_db_client=staging_main_db_client)

    # make response
    return Res200(
        message="success",
        data=data
    )


@operation.post("/rollback", response_model=Res200)
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
    return Res200(message="success")
