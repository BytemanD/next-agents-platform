import time

import httpx
from pystonic.utils import httpclient

from nap_client.common.objects import TokenResp


class AuthPluginV1(httpx.Auth):
    TOKEN_REFRESH_INTERVAL = 1800

    def __init__(self, base_url: str, username: str, password: str):
        self.username = username
        self.password = password

        self._client = httpclient.default_client(base_url, raise_for_status=True)
        self._token: str = ""
        self._token_issue_at: float | None = None

    def _get_token(self):
        if (
            not self._token_issue_at
            or time.time() - self._token_issue_at >= self.TOKEN_REFRESH_INTERVAL
        ):
            resp = self._client.post(
                "/api/v1/auth/login",
                json={"username": self.username, "password": self.password},
            )
            token_resp = TokenResp.model_validate(resp.json())
            self._token = token_resp.token
            self._token_issue_at = time.time()
        return self._token

    def get_token(self) -> str:
        """返回当前 token；不存在或已超过刷新间隔时自动登录。"""
        return self._get_token()

    def auth_flow(self, request: httpx.Request):
        request.headers["authorization"] = f"Bearer {self._get_token()}"
        yield request
