from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

# from nap.master.api.v1 import doc, project, session
from nap.master.api.v1 import (
    agents,
    knowledge,
    knowledge_base,
    llms,
    monitoring,
    sessions,
    users,
)
from nap.master.manager import MANAGER
from pystonic.orm.database import create_all_tables
from pystonic.asgi.app import create_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Master ...")
    create_all_tables()
    MANAGER.start()
    yield
    logger.info("stop Master ...")
    MANAGER.stop()


APP = create_app(lifespan=lifespan)


for module in (agents, knowledge, knowledge_base, llms, users, sessions, monitoring):
    APP.include_router(module.router, prefix="/api/v1")
