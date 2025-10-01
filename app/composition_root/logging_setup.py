# logging_setup.py
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_fmt": {
            "format": "%(levelname).1s %(asctime)s %(name)s:%(lineno)d | %(message)s"
        },
        "file_fmt": {
            "format": "%(asctime)s %(levelname)s %(name)s %(process)d %(threadName)s | %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console_fmt",
        },
        "file_rotating": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "file_fmt",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 2_000_000,   # ~2MB per file
            "backupCount": 5,        # keep last 5 files
            "encoding": "utf-8",
        },
    },
    "root": {  # affects libraries too; keep at WARNING to avoid spam
        "level": "INFO",
        "handlers": ["console", "file_rotating"],
    },
    # Example: make your package more verbose than the root
    "loggers": {
        "myapp": { "level": "DEBUG", "propagate": True },
    },
}

def setup_logging():
    logging.config.dictConfig(CONFIG)

def get_logger(name: str | None = None) -> logging.Logger:
    """
    Use get_logger(__name__) inside modules.
    Ensures setup() was called once in your app entrypoint.
    """
    return logging.getLogger(name)
