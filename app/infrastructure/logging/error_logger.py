import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIRECTORY / "error.log"

error_logger = logging.getLogger(
    "api_error_logger"
)

error_logger.setLevel(logging.INFO)
error_logger.propagate = False

if not error_logger.handlers:
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)

    error_logger.addHandler(handler)