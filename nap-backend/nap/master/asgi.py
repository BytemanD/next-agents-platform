from contextlib import asynccontextmanager

import bcrypt
import dotenv
from fastapi import FastAPI
from loguru import logger
from nap.db.models import User
from nap.master.agent.asyncio import get_checkpointer_saver
from nap.master.api.v1 import (
    agents,
    attachment,
    dashboard,
    knowledge,
    knowledge_base,
    llms,
    mcps,
    monitoring,
    sessions,
    tools,
    users,
)
from nap.master.manager import MANAGER
from pystonic.asgi.app import create_app
from pystonic.asgi.middlewares.trace import TraceIdMiddleware
from pystonic.asgi.plugins import auth
from pystonic.common import log
from pystonic.orm.database import create_all_tables
from starlette.authentication import AuthenticationError

dotenv.load_dotenv()
log.setup_logger(remove=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Master ...")
    create_all_tables()

    async with get_checkpointer_saver() as saver:
        await MANAGER.setup(saver)
        await MANAGER.start()
        yield

    logger.info("stop Master ...")
    await MANAGER.stop()


APP = create_app(
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


for module in (
    agents,
    dashboard,
    knowledge,
    knowledge_base,
    llms,
    users,
    sessions,
    tools,
    monitoring,
    attachment,
    mcps,
):
    APP.include_router(module.router, prefix="/api/v1")


def _on_login(username: str, password: str):
    users = User.query(User.username == username)
    if not users:
        raise AuthenticationError("user not exists")
    if not bcrypt.checkpw(password.encode(), users[0].password.encode()):
        raise AuthenticationError("username or password error")


APP.add_middleware(TraceIdMiddleware)
auth.setup(
    APP,
    on_login=_on_login,
    exclude_routes={
        ("POST", "/api/v1/users"),
        ("GET", "/api/docs"),
        ("GET", "/api/redoc"),
        ("GET", "/api/openapi.json"),
    },
)
