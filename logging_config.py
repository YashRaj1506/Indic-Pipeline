
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger()        
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    fh = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
