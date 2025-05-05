import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('agent:mon-system')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler("logger/logs_mon_system.log", maxBytes=30000000, backupCount=2, encoding="utf-8-sig")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger_monitoring = setup_logger()
