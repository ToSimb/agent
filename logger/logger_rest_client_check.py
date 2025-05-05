import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('agent:rest-client-check')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler("logger/logs_rest_client_check.log", maxBytes=30000000, backupCount=3, encoding="utf-8-sig")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger_rest_client_check = setup_logger()
