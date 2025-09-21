__all__ = [
    "logger",
    "LoggerService",
    "get_logger",
]

import logging
import sys
from typing import Dict

from src.core import constants


class Constants(constants.Constants):
    pass


class LoggerService:
    """A logger service that supports both global and named logger instances."""

    _instances: Dict[str, "LoggerService"] = {}
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls, name: str = Constants.GLOBAL_LOGGER_NAME) -> "LoggerService":
        """Create or return existing logger instance for the given name."""
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, name: str = "stride_lens_logger"):
        """Initialize the logger if not already initialized."""
        self.name = name
        if name not in self._loggers:
            self._setup_logger(name)

    def _setup_logger(self, name: str) -> None:
        """Set up the logger with appropriate handlers and formatting."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            self._loggers[name] = logger
            return

        formatter = logging.Formatter(
            f"%(asctime)s - {name} - %(levelname)s - %(filename)s:%(lineno)d - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self._loggers[name] = logger

    @property
    def _logger(self) -> logging.Logger:
        """Get the logger instance for this service."""
        return self._loggers[self.name]

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log a critical message."""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception with traceback."""
        self._logger.exception(message, *args, **kwargs)

    def set_level(self, level: str) -> None:
        """Set the logging level."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if level.upper() in level_map:
            self._logger.setLevel(level_map[level.upper()])


logger = LoggerService()


def get_logger(name: str = Constants.GLOBAL_LOGGER_NAME) -> LoggerService:
    """Get a logger instance with a specific name."""
    return LoggerService(name)
