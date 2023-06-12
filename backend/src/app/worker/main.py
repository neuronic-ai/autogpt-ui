import logging

from arq import func
from arq.connections import RedisSettings
from loguru import logger
from prisma import Prisma

from app.core import settings, init_logging
from .tasks import run_auto_gpt


prisma = Prisma(auto_register=True)


async def startup(ctx) -> None:
    await prisma.connect()
    init_logging.init_logging(level=logging.INFO)
    logger.info("Worker is ready")


async def shutdown(ctx) -> None:
    await prisma.disconnect()


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli
class WorkerSettings:
    functions = [
        func(run_auto_gpt.run, name="run_auto_gpt", timeout=60 * 60 * 24),  # type: ignore
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    allow_abort_jobs = True
