from arq.jobs import Job
from loguru import logger

from app.core import globals


async def abort_job(job_id: str) -> None:
    try:
        await Job(job_id, globals.arq_redis).abort(timeout=0, poll_delay=0.01)
    except Exception as e:
        logger.warning(f"An error occurred while aborting job: {e}")
