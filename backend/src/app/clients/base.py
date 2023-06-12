from abc import ABC, abstractmethod
from typing import Any

import aiohttp
from furl import furl


class BaseClient(ABC):
    def __init__(self, base_url: str | None = None, api_key: str | None = None, *args: Any, **kwargs: Any):
        self.furl = furl(base_url or self.default_url)
        self.api_key = api_key

    @property
    @abstractmethod
    def default_url(self) -> str:
        ...

    @property
    def api_key_header(self) -> str:
        return ""

    @property
    def default_rate_limit(self) -> int | None:
        return None

    @property
    def default_rate_period(self) -> int:
        return 1

    async def _fetch(
        self,
        path: str,
        method: str = "get",
        raise_for_status: bool = False,
        **params: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        headers = params.pop("headers", {})
        if self.api_key and self.api_key_header:
            headers[self.api_key_header] = self.api_key
        async with aiohttp.ClientSession() as session:
            r = await session.request(method, str(self.furl / path), headers=headers, **params)
            if raise_for_status:
                r.raise_for_status()
            return await r.json(content_type=None)
