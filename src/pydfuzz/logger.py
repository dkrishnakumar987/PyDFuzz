import os
import sys
from loguru import logger as log


def configure_logger():
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_dir = os.path.join(src_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    log.remove()
    log.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )
    log.add(
        os.path.join(log_dir, "pydfuzz.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="DEBUG",
        rotation="500 MB",
    )
    log.add(
        os.path.join(log_dir, "pydfuzz_error.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="ERROR",
        rotation="500 MB",
    )


configure_logger()

logger = log
