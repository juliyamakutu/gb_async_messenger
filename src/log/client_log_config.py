import logging
import os
import sys

from config import client_config as config

_format = logging.Formatter(config.log_format)

log_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client.log")

_console_handler = logging.StreamHandler(sys.stderr)
_file_handler = logging.FileHandler(log_filename, encoding=config.encoding)
_file_handler.setFormatter(_format)
_console_handler.setFormatter(_format)

logger = logging.getLogger("amsg.client")
logger.setLevel(config.log_level)
logger.addHandler(_file_handler)
logger.addHandler(_console_handler)

if __name__ == "__main__":
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
