import logging
import logging.config
from pathlib import Path


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level


LOG_FILE = Path(__file__).resolve().parents[1] / "app.log"
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "info_only": {
            "()": "backend.core.logger.MaxLevelFilter",
            "max_level": logging.INFO,
        }
    },
    "formatters": {
        "basic": {
            "format": "%(asctime)s %(levelname)s %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
        },
    },
    "handlers": {
        "stderr_info": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "basic",
            "filters": ["info_only"],
            "stream": "ext://sys.stdout",
        },
        "stderr_warnings_and_errors": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": str(LOG_FILE),
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["stderr_info", "stderr_warnings_and_errors", "file"],
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
