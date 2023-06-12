import logging

from loguru import logger
from gunicorn import glogging  # type: ignore


class Logger(glogging.Logger):
    """Implements and overrides the gunicorn logging interface.
    This class inherits from the standard gunicorn logger and overrides it by
    replacing the handlers with `InterceptHandler` in order to route the
    gunicorn logs to loguru.
    """

    def __init__(self, cfg):
        super().__init__(cfg)
        logging.getLogger("gunicorn.error").handlers = [InterceptHandler()]
        logging.getLogger("gunicorn.access").handlers = [InterceptHandler()]


class InterceptHandler(logging.Handler):
    """Handler for intercepting records and outputting to loguru."""

    def emit(self, record: logging.LogRecord):
        """Intercepts log messages.
        Intercepts log records sent to the handler, adds additional context to
        the records, and outputs the record to the default loguru logger.
        Args:
            record: The log record
        """
        level: int | str = ""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    for _, _logger in logging.root.manager.loggerDict.items():
        if not isinstance(_logger, logging.PlaceHolder):
            if _logger.handlers:
                for _handler in _logger.handlers:
                    _logger.removeHandler(_handler)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.configure(
        handlers=[
            {
                "sink": handler,
                "format": "[{time:YYYY-MM-DD HH:mm:ss,SSS}] [{process}] [{level}] {message}",
                "level": level,
                # "backtrace": False,
                # "diagnose": False,
            }
        ],
    )
