import os
from time import time
from datetime import timedelta

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from helper.llm import *
from models.llm import *
from utils.constants import *
from utils.error import *
from utils.constants import DOCKER, DOCKER_LOCAL
from client import OpenAIClient, AzureClient, BedrockClient, AnthropicClient, FourgritClient, LocalClient, XClient, GoogleClient



llm = APIRouter(prefix="/llm")



@llm.post("/chat")
async def chat(payload: ChatPayload):
    try:
        # time test
        if payload.time:
            time_req_from_backend = time()
            elapsed = timedelta(seconds=int(time_req_from_backend - payload.time))
            logging.info(f"session_key: {payload.session_key} | [TIMETEST] ⏱️ TIME from backend: {elapsed}")

        # check token length
        check_token_length(payload)

        # check image file
        if payload.images:
            payload.images = [clear_data_in_base64(text) for text in payload.images]
            if not payload.image_types:
                payload.image_types = [detect_image_type(image) for image in payload.images]
            else:
                check_is_in_only_base64_and_url(payload.image_types)
            # if BASE64 in set(payload.image_types):
            #     payload.image_filename_extensions = await get_image_extension(payload.images, payload.image_types)

        # check vendor and create llm client
        server_stage = os.getenv("SERVER_STAGE")
        if server_stage == DOCKER_LOCAL:
            logging.info(f"session_key: {payload.session_key} | [api.llm.chat] activate local_client")
            local_client = LocalClient(payload)
            first_try_client = local_client
            second_try_client = local_client
        elif server_stage == DOCKER:
            logging.info(f"session_key: {payload.session_key} | [api.llm.chat] activate 4grit_client")
            first_try_client = FourgritClient(payload)
            second_try_client = FourgritClient(payload)
        else:
            logging.info(f"session_key: {payload.session_key} | [api.llm.chat] activate major supply vendor client")
            openai_client = OpenAIClient(payload)
            azure_client = AzureClient(payload)
            bedrock_client = BedrockClient(payload)
            anthropic_client = AnthropicClient(payload)
            x_client = XClient(payload)
            google_client = GoogleClient(payload)
            first_try_client, second_try_client = set_client(payload, openai_client, azure_client, bedrock_client, anthropic_client, x_client, google_client)

        logging.info(f"session_key: {payload.session_key} | [api.llm.chat] complete to calling set_client")

        if payload.stream:
            return StreamingResponse(
                safe_stream(first_try_client, second_try_client),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream; charset=utf-8",
                    "Cache-Control": "no-cache",
                    "Transfer-Encoding": "chunked"
                }
            )
        else:
            result = await safe_chat(first_try_client, second_try_client)
            return ORJSONResponse(result)

    except ProxyServerError as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat] error: {e.message}")
        return ORJSONResponse(
            content={"error": str(e.message)},
            status_code=599
        )
    except OverTokenLimitError as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat] error: {e}")
        return ORJSONResponse(
            content={"error": str(e.message)},
            status_code=599
        )
    except Exception as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat] error: {e}")
        return ORJSONResponse(
            content={"error": str(e)},
            status_code=599
        )


@llm.post("/chat_mcp")
async def chat_mcp(payload: ChatMCPPayload):
    try:
        # time test
        if payload.time:
            time_req_from_backend = time()
            elapsed = timedelta(seconds=int(time_req_from_backend - payload.time))
            logging.info(f"session_key: {payload.session_key} | [TIMETEST] ⏱️ TIME from backend: {elapsed}")

        #check token length
        check_token_length(payload)

        # check vendor and create llm client
        if payload.service == VLLM or payload.vendor == FOURGRIT:
            logging.info(f"session_key: {payload.session_key} | [api.llm.chat_mcp] activate fourgrit_client")
            fourgrit_client = FourgritClient(payload)
            first_try_client = fourgrit_client
            second_try_client = fourgrit_client
        else:
            logging.info(f"session_key: {payload.session_key} | [api.llm.chat_mcp] activate major supply vendor client")
            anthropic_client = AnthropicClient(payload)
            bedrock_client = BedrockClient(payload)
            google_client = GoogleClient(payload)
            # local_client = LocalClient(payload)
            first_try_client, second_try_client = set_mcp_client(payload, bedrock_client, anthropic_client, google_client)
        logging.info(f"session_key: {payload.session_key} | [api.llm.chat_mcp] complete to calling set_client")
        return StreamingResponse(
            safe_stream_with_mcp(first_try_client, second_try_client),
            media_type="text/event-stream",
            headers={
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache",
                "Transfer-Encoding": "chunked"
            }
        )

    except ProxyServerError as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat_mcp] error: {e}")
        return ORJSONResponse(
            content={"error": str(e)},
            status_code=599
        )
    except OverTokenLimitError as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat_mcp] error: {e}")
        return ORJSONResponse(
            content={"error": str(e)},
            status_code=599
        )
    except Exception as e:
        logging.error(f"session_key: {payload.session_key} | [api.llm.chat_mcp] error: {e}")
        return ORJSONResponse(
            content={"error": str(e)},
            status_code=599
        )


@llm.post("/embeddings")
@handle_errors()
async def embeddings(payload: EmbeddingsPayload):
    # check vendor and create llm client
    if payload.debug_id:
        logging.info(f"[api.llm.embeddings] debugId: {payload.debug_id}")

    server_stage = os.getenv("SERVER_STAGE")

    if server_stage == DOCKER_LOCAL:
        local_client = LocalClient(payload)
        first_client = local_client
        second_client = local_client
    elif server_stage == DOCKER:
        fourgrit_client = FourgritClient(payload)
        first_client = fourgrit_client
        second_client = fourgrit_client
    else:
        first_client = OpenAIClient(payload)
        second_client = AzureClient(payload)

    vectors = await safe_embeddings(first_client, second_client)

    if payload.debug_id:
        return ORJSONResponse({
            "vectors": vectors,
            "debugId": payload.debug_id
        })
    else:
        return ORJSONResponse(vectors)
