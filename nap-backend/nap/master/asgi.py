from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

# from nap.master.api.v1 import doc, project, session
from nap.master.api.v1 import agents, knowledge, knowledge_base, llms, sessions, users
from pystonic.orm.database import create_all_tables
from pystonic.asgi.app import create_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Master ...")
    create_all_tables()
    yield
    logger.info("stop Master ...")


APP = create_app(lifespan=lifespan)


for module in (agents, knowledge, knowledge_base, llms, users, sessions):
    APP.include_router(module.router, prefix="/api/v1")
