"""
utils/logger.py
Centralised logger factory – call setup_logger() once at startup,
then use logging.getLogger("coupon_bot") anywhere in the project.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_LOGGER_NAME = "coupon_bot"

_configured = False


def setup_logger() -> logging.Logger:
    """
    Configure and return the application logger.

    Safe to call multiple times – subsequent calls are no-ops and just
    return the already-configured logger.
    """
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)

    if _configured:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── File handler (rotating) ────────────────────────────────────────
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    log_path = os.path.join(settings.LOG_DIR, "app.log")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )

    # ── Console handler ────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _configured = True
    return logger


def get_logger() -> logging.Logger:
    """Return the application logger (must call setup_logger() first)."""
    return logging.getLogger(_LOGGER_NAME)