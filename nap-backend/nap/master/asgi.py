from contextlib import asynccontextmanager

import bcrypt
from fastapi import FastAPI
from loguru import logger
from nap.db.models import User
from nap.master.api.v1 import (
    agents,
    knowledge,
    knowledge_base,
    llms,
    monitoring,
    sessions,
    tools,
    users,
)
from nap.master.manager import MANAGER
from pystonic.asgi.app import create_app
from pystonic.asgi.middlewares.trace import TraceIdMiddleware
from pystonic.asgi.plugins import auth
from pystonic.common.log import setup_logger
from pystonic.orm.database import create_all_tables
from starlette.authentication import AuthenticationError

setup_logger(remove=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("start Master ...")
    create_all_tables()
    await MANAGER.start()
    await MANAGER.init_agent()
    yield
    logger.info("stop Master ...")
    await MANAGER.stop()


APP = create_app(lifespan=lifespan)


for module in (
    agents,
    knowledge,
    knowledge_base,
    llms,
    users,
    sessions,
    tools,
    monitoring,
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
        ("GET", "/docs"),
        ("GET", "/openapi.json"),
    },
)
