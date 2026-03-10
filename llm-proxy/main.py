# default lib
import os
from utils.constants import *
if os.getenv("SERVER_STAGE") not in DOCKER_LIST:
    from dotenv import load_dotenv
    # load .env & set root path
    APP_ROOT = os.path.dirname(__file__)
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path, override=True)
import logging

# fast-api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# route
from api.llm import llm
from api.file import file



# setup logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# api setting
app = FastAPI()
app.include_router(llm)
app.include_router(file)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origin=ALLOWED_API_ADDRESS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run API server
if __name__ == "__main__":
    uvicorn.run(
        "main:app", # app=app,
        host="0.0.0.0",
        port=9999,
        timeout_keep_alive=300,
        limit_concurrency=2500,
        limit_max_requests=5000,
        loop="asyncio",
        http="httptools", # httptools = 성능우선, 프로덕션 환경에선 얘 써야함
        log_level="info",
        reload=True
    )
