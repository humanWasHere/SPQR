from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

load_dotenv()
ENVIRONMENT = os.getenv('ENVIRONMENT')


if ENVIRONMENT == 'development':
    log_file_path = Path(__file__).resolve().parents[2] / "spqr.log"
elif ENVIRONMENT == 'production':
    log_file_path = Path.home() / "tmp" / "spqr.log"
else:
    raise ValueError(f"Unknown environment: {ENVIRONMENT}")


def logger_init(log_file=log_file_path, log_level=logging.INFO, max_bytes=2500, backup_count=1):
    # TODO max_bytes seems not to work
    # strange fix : https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    """
    Initialise et configure le logger de l'application.

    :param log_file: Nom du fichier de log.
    :param log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    :param max_bytes: Taille maximale du fichier de log avant rotation.
    :param backup_count: Nombre de fichiers de sauvegarde à conserver.
    :return: Logger configuré.
    """
    log_file.parent.mkdir(exist_ok=True)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s', datefmt='%m/%d/%Y %H:%M:%S %p',
                        handlers=[
                            RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count),
                            logging.StreamHandler()
                        ])
    # logger.propagate = False # to avoid double printing
