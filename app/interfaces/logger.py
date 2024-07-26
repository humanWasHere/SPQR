import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def logger_init(log_file=Path(__file__).resolve().parents[2] / "spqr.log", log_level=logging.INFO, max_bytes=2000, backup_count=0):
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
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s', datefmt='%m/%d/%Y %H:%M:%S %p',
                        handlers=[
                            RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count),
                            logging.StreamHandler()
                        ])
    # logger.propagate = False # to avoid double printing
