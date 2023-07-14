from unittest.mock import patch

import pytest
from async_asgi_testclient import TestClient

from app.core import settings
from app.clients import AuthBackendClient

from tests.helpers.auth_backend_mocker import session_payload


pytestmark = pytest.mark.asyncio


async def test_check_session_no_auth(async_client: TestClient):
    r = await async_client.get(f"{settings.API_V1_STR}/sessions/check")
    assert 204 == r.status_code


async def test_check_session_auth_success(async_client: TestClient, with_auth):
    with patch.object(AuthBackendClient, "get_session", return_value=session_payload()):
        r = await async_client.get(
            f"{settings.API_V1_STR}/sessions/check", cookies={settings.SESSION_COOKIE: "session"}
        )
        assert 204 == r.status_code


async def test_check_session_auth_fail(async_client: TestClient, with_auth):
    with patch.object(AuthBackendClient, "get_session", return_value={}):
        r = await async_client.get(
            f"{settings.API_V1_STR}/sessions/check", cookies={settings.SESSION_COOKIE: "session"}
        )
        assert 401 == r.status_code
