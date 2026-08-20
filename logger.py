"""
logger.py
Shared logger factory. Every module should call get_logger(__name__)
instead of configuring logging itself, so log level and format stay
consistent across the app.
"""

import logging
import os
import sys

from src.utils.config import get_settings

_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    os.makedirs(_LOG_DIR, exist_ok=True)
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    file_handler = logging.FileHandler(_LOG_FILE)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger, configuring the root logger on first use."""
    _configure_root_logger()
    return logging.getLogger(name)
