from __future__ import annotations

import logging
import logging.handlers
import functools
import threading
import time
import traceback
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

from backend.core.config import (
    APP_NAME,
    LOG_DIR,
    LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
)

# =====================================================
# LOG DIRECTORY
# =====================================================

LOG_DIR.mkdir(

    parents=True,

    exist_ok=True,

)

# =====================================================
# COLORS
# =====================================================

RESET = "\033[0m"

COLORS = {

    logging.DEBUG: "\033[36m",

    logging.INFO: "\033[32m",

    logging.WARNING: "\033[33m",

    logging.ERROR: "\033[31m",

    logging.CRITICAL: "\033[41m",

}

# =====================================================
# FORMATTER
# =====================================================

class ColoredFormatter(

    logging.Formatter,

):

    def format(

        self,

        record,

    ):

        message = super().format(

            record

        )

        color = COLORS.get(

            record.levelno,

            "",

        )

        return f"{color}{message}{RESET}"

# =====================================================
# LOGGER MANAGER
# =====================================================

class LoggerManager:

    _instance = None

    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(

        cls,

    ):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(

                    cls

                )

        return cls._instance

    # -------------------------------------------------

    def __init__(

        self,

    ):

        if getattr(

            self,

            "_initialized",

            False,

        ):

            return

        self._initialized = True

        self.loggers = {}

        self.configure_root()

    # =====================================================
    # ROOT LOGGER
    # =====================================================

    def configure_root(

        self,

    ):

        root = logging.getLogger()

        if root.handlers:

            return

        root.setLevel(

            getattr(

                logging,

                LOG_LEVEL,

            )

        )

        # ------------------------------

        console = logging.StreamHandler()

        console.setFormatter(

            ColoredFormatter(

                LOG_FORMAT

            )

        )

        # ------------------------------

        file_handler = logging.handlers.TimedRotatingFileHandler(

            filename=str(LOG_FILE),

            when="midnight",

            interval=1,

            backupCount=30,

            encoding="utf-8",

        )

        file_handler.setFormatter(

            logging.Formatter(

                LOG_FORMAT

            )

        )

        root.addHandler(

            console

        )

        root.addHandler(

            file_handler

        )

    # =====================================================
    # LOGGER
    # =====================================================

    def get_logger(

        self,

        name,

    ):

        if name in self.loggers:

            return self.loggers[name]

        logger = logging.getLogger(

            name

        )

        self.loggers[name] = logger

        return logger

# =====================================================
# GLOBAL LOGGER
# =====================================================

logger_manager = LoggerManager()

logger = logger_manager.get_logger(

    APP_NAME

)

# =====================================================
# DECORATOR
# =====================================================

def log_calls(

    level=logging.DEBUG,

):

    def decorator(

        func,

    ):

        @functools.wraps(

            func

        )

        def wrapper(

            *args,

            **kwargs,

        ):

            log = logger_manager.get_logger(

                func.__module__

            )

            log.log(

                level,

                f"Entering {func.__name__}",

            )

            result = func(

                *args,

                **kwargs,

            )

            log.log(

                level,

                f"Leaving {func.__name__}",

            )

            return result

        return wrapper

    return decorator
# =====================================================
# PERFORMANCE DECORATOR
# =====================================================

def log_execution_time(

    level=logging.INFO,

):

    def decorator(

        func,

    ):

        @functools.wraps(

            func

        )

        def wrapper(

            *args,

            **kwargs,

        ):

            log = logger_manager.get_logger(

                func.__module__

            )

            start = time.perf_counter()

            try:

                return func(

                    *args,

                    **kwargs,

                )

            finally:

                elapsed = (

                    time.perf_counter()

                    - start

                ) * 1000

                log.log(

                    level,

                    f"{func.__name__} executed in "

                    f"{elapsed:.2f} ms",

                )

        return wrapper

    return decorator


# =====================================================
# EXCEPTION DECORATOR
# =====================================================

def log_exceptions(

    reraise=True,

):

    def decorator(

        func,

    ):

        @functools.wraps(

            func

        )

        def wrapper(

            *args,

            **kwargs,

        ):

            log = logger_manager.get_logger(

                func.__module__

            )

            try:

                return func(

                    *args,

                    **kwargs,

                )

            except Exception:

                log.error(

                    "Unhandled exception in %s\n%s",

                    func.__name__,

                    traceback.format_exc(),

                )

                if reraise:

                    raise

                return None

        return wrapper

    return decorator


# =====================================================
# TIMER CONTEXT
# =====================================================

@contextmanager
def timer(

    name="Operation",

    level=logging.INFO,

):

    log = logger_manager.get_logger(

        "Timer"

    )

    start = time.perf_counter()

    try:

        yield

    finally:

        elapsed = (

            time.perf_counter()

            - start

        ) * 1000

        log.log(

            level,

            f"{name} completed in "

            f"{elapsed:.2f} ms",

        )


# =====================================================
# SIMPLE LOG HELPERS
# =====================================================

def debug(

    message,

    *args,

):

    logger.debug(

        message,

        *args,

    )


def info(

    message,

    *args,

):

    logger.info(

        message,

        *args,

    )


def warning(

    message,

    *args,

):

    logger.warning(

        message,

        *args,

    )


def error(

    message,

    *args,

):

    logger.error(

        message,

        *args,

    )


def critical(

    message,

    *args,

):

    logger.critical(

        message,

        *args,

    )


def exception(

    message,

):

    logger.exception(

        message,

    )


# =====================================================
# THREAD UTILITIES
# =====================================================

def thread_logger():

    thread_name = threading.current_thread().name

    return logger_manager.get_logger(

        f"Thread:{thread_name}"

    )


# =====================================================
# LOGGER STATISTICS
# =====================================================

class LoggerStatistics:

    def __init__(

        self,

    ):

        self.started = datetime.now()

        self.messages = 0

    # ---------------------------------------------

    def increment(

        self,

    ):

        self.messages += 1

    # ---------------------------------------------

    @property
    def uptime(self):

        return (

            datetime.now()

            - self.started

        )

    # ---------------------------------------------

    def to_dict(

        self,

    ):

        return {

            "started": self.started,

            "uptime": str(

                self.uptime

            ),

            "messages": self.messages,

            "registered_loggers": len(

                logger_manager.loggers

            ),

        }


logger_stats = LoggerStatistics()


# =====================================================
# LOG FILE UTILITIES
# =====================================================

def current_log_file():

    return LOG_FILE


def log_directory():

    return LOG_DIR


def log_exists():

    return LOG_FILE.exists()


def log_size():

    if not LOG_FILE.exists():

        return 0

    return LOG_FILE.stat().st_size


def clear_log():

    if LOG_FILE.exists():

        LOG_FILE.write_text(

            "",

            encoding="utf-8",

        )

        logger.info(

            "Log file cleared."

        )
        # =====================================================
# LOG CLEANUP
# =====================================================

def cleanup_logs(

    keep=30,

):

    """
    Delete old rotated log files while
    keeping the newest 'keep' files.
    """

    files = sorted(

        LOG_DIR.glob(

            "stockversity.log*"

        ),

        key=lambda f: f.stat().st_mtime,

        reverse=True,

    )

    removed = 0

    for file in files[keep:]:

        try:

            file.unlink()

            removed += 1

        except Exception as exc:

            logger.warning(

                "Unable to delete log file %s : %s",

                file,

                exc,

            )

    logger.info(

        "Log cleanup complete. Removed %d files.",

        removed,

    )

    return removed


# =====================================================
# RESET LOGGER
# =====================================================

def reset_logging():

    """
    Removes all handlers and
    reconfigures the root logger.
    """

    root = logging.getLogger()

    for handler in root.handlers[:]:

        handler.close()

        root.removeHandler(

            handler

        )

    logger_manager.loggers.clear()

    logger_manager.configure_root()

    logger.info(

        "Logging system restarted."

    )


# =====================================================
# DIAGNOSTICS
# =====================================================

def diagnostics():

    return {

        "application": APP_NAME,

        "log_file": str(

            LOG_FILE

        ),

        "log_directory": str(

            LOG_DIR

        ),

        "log_exists": log_exists(),

        "log_size": log_size(),

        "registered_loggers": list(

            logger_manager.loggers.keys()

        ),

        "statistics": logger_stats.to_dict(),

    }


# =====================================================
# STARTUP / SHUTDOWN
# =====================================================

def startup_banner():

    logger.info(

        "=" * 70

    )

    logger.info(

        "%s v%s",

        APP_NAME,

        "4.0",

    )

    logger.info(

        "Logging initialized."

    )

    logger.info(

        "Log File : %s",

        LOG_FILE,

    )

    logger.info(

        "Started : %s",

        datetime.now().strftime(

            "%d-%m-%Y %H:%M:%S"

        ),

    )

    logger.info(

        "=" * 70

    )


def shutdown():

    logger.info(

        "=" * 70

    )

    logger.info(

        "Application shutting down."

    )

    logger.info(

        "Uptime : %s",

        logger_stats.uptime,

    )

    logger.info(

        "Messages Logged : %d",

        logger_stats.messages,

    )

    logger.info(

        "=" * 70

    )

    logging.shutdown()


# =====================================================
# LOGGER ADAPTER
# =====================================================

class AppLogger:

    """
    Lightweight wrapper around the
    standard logger to automatically
    count emitted log messages.
    """

    def __init__(

        self,

        name=APP_NAME,

    ):

        self._logger = logger_manager.get_logger(

            name

        )

    # ---------------------------------------------

    def debug(

        self,

        message,

        *args,

    ):

        logger_stats.increment()

        self._logger.debug(

            message,

            *args,

        )

    # ---------------------------------------------

    def info(

        self,

        message,

        *args,

    ):

        logger_stats.increment()

        self._logger.info(

            message,

            *args,

        )

    # ---------------------------------------------

    def warning(

        self,

        message,

        *args,

    ):

        logger_stats.increment()

        self._logger.warning(

            message,

            *args,

        )

    # ---------------------------------------------

    def error(

        self,

        message,

        *args,

    ):

        logger_stats.increment()

        self._logger.error(

            message,

            *args,

        )

    # ---------------------------------------------

    def critical(

        self,

        message,

        *args,

    ):

        logger_stats.increment()

        self._logger.critical(

            message,

            *args,

        )

    # ---------------------------------------------

    def exception(

        self,

        message,

    ):

        logger_stats.increment()

        self._logger.exception(

            message,

        )


app_logger = AppLogger()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "logger",
    "app_logger",
    "logger_manager",
    "logger_stats",

    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",

    "log_calls",
    "log_execution_time",
    "log_exceptions",

    "timer",

    "thread_logger",

    "current_log_file",
    "log_directory",
    "log_exists",
    "log_size",
    "clear_log",
    "cleanup_logs",

    "diagnostics",

    "startup_banner",
    "shutdown",

    "reset_logging",

    "AppLogger",
    "LoggerManager",
]