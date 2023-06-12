from enum import Enum
from typing import Optional

from .base import BaseClient


class RequestType(str, Enum):
    email = "email"
    openai = "openai"
    user = "user:"
    userdata = "userdata:"


class AuthBackendClient(BaseClient):
    default_url = ""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        session_path: str = "/session",
        user_path: str = "/user",
        session_cookie: str = "sessionId",
    ):
        super().__init__(base_url, api_key)
        self.session_path = session_path
        self.user_path = user_path
        self.session_cookie = session_cookie

    async def get_session(self, session_id: Optional[str] = None) -> dict[str, dict[str, str]]:
        cookies = {}
        if session_id:
            cookies = {self.session_cookie: session_id}
        return await self._fetch(
            self.session_path,
            cookies=cookies,
        )

    async def get_user(
        self, request_type: RequestType, session_id: Optional[str] = None, username: Optional[str] = None
    ) -> dict[str, str]:
        headers = {"requesttype": request_type.value}
        cookies = {}
        params = {}
        if session_id:
            cookies = {self.session_cookie: session_id}
        if username:
            params["user"] = username
        return await self._fetch(
            self.user_path,
            headers=headers,
            params=params,
            cookies=cookies,
        )
