from abc import ABC, abstractmethod
from typing import NoReturn, Optional

from fastapi import HTTPException, Request, status
from prisma.models import User

from app.clients import AuthBackendClient
from app.core.config import settings

BAD_CREDENTIALS_MSG = "Could not validate credentials"
NO_PRIVILEGES_MSG = "The user doesn't have enough privileges"


class AuthDependency(ABC):
    @abstractmethod
    async def __call__(self, *args, **kwargs) -> User:
        pass

    def raise_401(self, detail: str = BAD_CREDENTIALS_MSG) -> NoReturn:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    def raise_403(self, detail: str = NO_PRIVILEGES_MSG) -> NoReturn:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    async def validate_user(self, user: User) -> User:
        return user


class NoAuthDependency(AuthDependency):
    async def __call__(self, request: Request) -> Optional[User]:
        user = await User.prisma().find_first(where={"id": 1})
        if not user:
            user = await User.prisma().upsert(
                where={"id": 1},
                data={
                    "create": {"id": 1, "username": "admin"},
                    "update": {"id": 1, "username": "admin"},
                },
            )
        return await self.validate_user(user)


class SessionAuthDependency(AuthDependency):
    async def __call__(self, request: Request) -> Optional[User]:
        client = AuthBackendClient(
            settings.SESSION_API_URL,
            user_path=settings.SESSION_API_USER_PATH,
            session_path=settings.SESSION_API_SESSION_PATH,
            session_cookie=settings.SESSION_COOKIE,
        )
        session_id = request.cookies.get(settings.SESSION_COOKIE)
        if not session_id:
            return self.raise_401()
        j = await client.get_session(session_id)
        if "user" not in j:
            return self.raise_401()
        user = await User.prisma().find_unique(where={"username": j["user"]["username"]})
        if not user:
            await User.prisma().upsert(
                where={"username": j["user"]["username"]},
                data={"create": {"username": j["user"]["username"]}, "update": {"username": j["user"]["username"]}},
            )
        return await self.validate_user(user)


auth_dependency = NoAuthDependency if settings.NO_AUTH else SessionAuthDependency
check_user = auth_dependency()
