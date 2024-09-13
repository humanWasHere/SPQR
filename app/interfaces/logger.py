from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

load_dotenv()
ENVIRONMENT = os.getenv('ENVIRONMENT')


if ENVIRONMENT == 'development':
    DEFAULT_LOG_PATH = Path(__file__).resolve().parents[2] / "spqr.log"
    LOG_LEVEL = logging.DEBUG
elif ENVIRONMENT == 'production':
    DEFAULT_LOG_PATH = Path.home() / "tmp" / "spqr.log"
    LOG_LEVEL = logging.INFO
else:
    raise EnvironmentError(f"Unknown environment: {ENVIRONMENT}")


def logger_init(log_file: str | Path = DEFAULT_LOG_PATH, log_level: int = LOG_LEVEL,
                max_bytes: int = 1024*1024, backup_count: int = 5) -> None:
    """
    Initializes and configures application logger.

    :param log_file: Log file name.
    :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    :param max_bytes: Maximum size of log file before rotation. A threshold.
    :param backup_count: Number of backup file to keep.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(module)-15s %(message)s ',
        datefmt='%d/%m/%Y %H:%M:%S',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count),
            logging.StreamHandler()
        ])
    # logger.propagate = False # to avoid double printing
    # TODO return logger object?


logger_init()
