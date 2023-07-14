import asyncio
from copy import deepcopy

import fakeredis.aioredis
import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient as AsyncTestClient

from app import create_app


pytestmark = pytest.mark.asyncio


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    import pytest

    mpatch = pytest.MonkeyPatch()

    import redis.asyncio

    mpatch.setattr(redis, "Redis", fakeredis.FakeRedis)
    mpatch.setattr(redis.asyncio, "Redis", fakeredis.aioredis.FakeRedis)


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> None:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncTestClient(create_app()) as client:
        yield client


@pytest_asyncio.fixture()
async def async_client_class(request, async_client):
    request.cls.async_client = async_client


@pytest.fixture
def with_no_auth():
    from app.core import settings
    from app.api.helpers.security import check_user, NoAuthDependency, SessionAuthDependency

    old_class = check_user.__class__
    settings.NO_AUTH = True
    NoAuthDependency.cast(check_user)
    yield
    settings.NO_AUTH = False
    old_class.cast(check_user)


@pytest.fixture
def with_auth():
    from app.core import settings
    from app.api.helpers.security import check_user, NoAuthDependency, SessionAuthDependency

    old_class = check_user.__class__
    settings.NO_AUTH = False
    SessionAuthDependency.cast(check_user)
    yield
    settings.NO_AUTH = True
    old_class.cast(check_user)
