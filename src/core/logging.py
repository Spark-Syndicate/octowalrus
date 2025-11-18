"""
Centralized logging configuration module.

This module provides a centralized logging setup that can be used throughout
the application. It supports different log formats for development and production
environments and integrates with the application settings.
"""

import logging
import sys
from typing import Literal, Optional
from datetime import datetime

from core.settings import settings

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        import json

        log_data = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            extra = getattr(record, "extra_fields")
            if isinstance(extra, dict):
                log_data.update(extra)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development environment."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get color for log level
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Format log message
        log_message = f"{color}[{record.levelname:8}]{reset} {timestamp} | "
        log_message += f"{record.name}:{record.funcName}:{record.lineno} | "
        log_message += f"{record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


def setup_logging(log_level: Optional[LogLevel] = None) -> None:
    """
    Configure the root logger with appropriate formatter and level.

    Args:
        log_level: Optional log level override. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.
                   If not provided, uses settings.log_level or defaults to INFO for production,
                   DEBUG for development.

    Raises:
        ValueError: If an invalid log level is provided.
    """
    # Determine log level
    if log_level is None:
        # Try to use settings.log_level first, fallback to environment-based defaults
        try:
            level = getattr(logging, settings.log_level.upper(), None)
            if level is None:
                raise ValueError(
                    f"Invalid log level: {settings.log_level}. "
                    f"Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
                )
        except (AttributeError, ValueError):
            # Fallback to environment-based defaults
            if settings.is_development:
                level = logging.DEBUG
            else:
                level = logging.INFO
    else:
        level = getattr(logging, log_level.upper(), None)
        if level is None:
            raise ValueError(
                f"Invalid log level: {log_level}. "
                f"Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Choose formatter based on environment
    if settings.is_production:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter(fmt="%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name. If not provided, uses the calling module's name.

    Returns:
        Configured logger instance.

    Example:
        ```python
        from core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Application started")
        ```
    """
    if name is None:
        # Try to get the caller's module name
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "root")
        else:
            name = "root"

    return logging.getLogger(name)
