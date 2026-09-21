from datetime import UTC, datetime, timedelta
from typing import Callable

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import jwt
from loguru import logger
from nap.common.conf import CONF
from pydantic import BaseModel, SecretStr
from starlette.requests import HTTPConnection, Request
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
    SimpleUser,
    UnauthenticatedUser,
)
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationError
from starlette import status
from pystonic.common import context
from starlette.responses import Response


class JWTToken(BaseModel):
    sub: str
    exp: datetime


class JWTService:
    def encode(self, user: str):
        payload = {"sub": user, "exp": datetime.now(UTC) + timedelta(hours=1)}
        return jwt.encode(payload, key=CONF.jwt.key, algorithm=CONF.jwt.algorithms[0])

    def decode(self, token: str, verify: bool = False):
        return jwt.decode(
            token, key=CONF.jwt.key, algorithms=CONF.jwt.algorithms, verify=verify
        )

    def verify(self, token: str):
        return JWTToken.model_validate(self.decode(token, verify=True))


JWT_SERVICE = JWTService()


class JWTBackend(AuthenticationBackend):
    def __init__(self, exclude_routes: set[tuple[str, str]] = set()) -> None:
        super().__init__()
        self.exclude_routes = exclude_routes

    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        if (conn.scope["method"], conn.url.path) in self.exclude_routes:
            return AuthCredentials(["authenticated"]), UnauthenticatedUser()

        auth_header = conn.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationError("Missing Authorization header")
        if auth_header.startswith(("Bearer ", "bearer ")):
            try:
                token = JWT_SERVICE.verify(token=auth_header.split(maxsplit=1)[1])
                context.set_account(token.sub)
                return AuthCredentials(["authenticated"]), SimpleUser(token.sub)
            except jwt.exceptions.PyJWTError as e:
                logger.error("auth faield: {}", e)
                raise AuthenticationError("Invalid token")
        raise AuthenticationError("Invalid token")


class LoginRequest(BaseModel):
    username: str
    password: SecretStr


class LoginResponse(BaseModel):
    token: str


def unauthorized_error(conn: HTTPConnection, exc: Exception) -> Response:
    return JSONResponse({"error": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED)


def setup(
    app: FastAPI,
    on_login: Callable[[str, str], None],
    login_url: str | None = "/api/v1/auth/login",
    exclude_routes: set[tuple[str, str]] | None = None,
):
    """安装 JWT 认证中间件
    Args:
        app: FastAPI app
        on_login: 用户名+密码登录的方法, 如果认证失败，抛出 AuthenticationError 异常
        login_url: 用户名+密码登录接口路由
        exclude_routes: 需要排除认证的路由
    """

    exclude_routes = exclude_routes or set([])
    if login_url:
        exclude_routes.update({("POST", login_url)})

        @app.post(login_url)
        def _login(req: Request, body: LoginRequest):
            try:
                on_login(body.username, body.password.get_secret_value())
            except AuthenticationError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
                )
            token = JWT_SERVICE.encode(body.username)
            logger.success("login success")
            return LoginResponse(token=token)

    app.add_middleware(
        AuthenticationMiddleware,
        backend=JWTBackend(exclude_routes=exclude_routes),
        on_error=unauthorized_error,
    )
