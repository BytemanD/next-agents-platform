from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from pystonic.orm.database import create_all_tables
from pystonic import log
from pystonic.asgi.app import create_app


from nap.knowledge.manager import MANAGER

log.setup_logger(remove=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Knowledge ...")
    create_all_tables()
    MANAGER.start()
    yield
    logger.info("stop Knowledge ...")


APP = create_app(lifespan=lifespan)
