import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(module_name: str) -> logging.Logger:
    """Erstellt einen logger für das angegebene Modul mit rotierender Logdatei."""
    log_path = os.path.join(LOG_DIR, f"{module_name}.log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=3
        )
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
