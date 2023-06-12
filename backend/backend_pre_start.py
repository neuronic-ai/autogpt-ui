import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

engine = create_engine(str(settings.DATABASE_URL).split("?")[0].replace("mysql://", "mysql+pymysql://"), convert_unicode=True)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    # Try to create session to check if DB is awake
    try:
        session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
        session.execute("SELECT 1")
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
