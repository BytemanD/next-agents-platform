from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI
from loguru import logger
from pystonic.asgi.app import create_app
from pystonic.common import log
from pystonic.orm.database import create_all_tables

from nap.knowledge.api.v1 import document, retrival
from nap.knowledge.manager import MANAGER

dotenv.load_dotenv()

log.setup_logger(remove=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Knowledge ...")
    create_all_tables()
    await MANAGER.start()
    yield
    logger.info("stop Knowledge ...")
    await MANAGER.stop()


APP = create_app(lifespan=lifespan)

for module in (retrival, document):
    APP.include_router(module.router, prefix="/api/v1")
