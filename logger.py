import logging
import os
from datetime import datetime

if not os.path.exists('log'):
    os.makedirs('log')

name = 'elk_bot'
log_date = None
handler = None


def create_logger():
    global handler
    global log_date
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.removeHandler(handler)
    log_date = datetime.now()
    log_file_name = os.path.join('log', '{}_{}.log'.format(name, log_date.strftime('%Y%m%d')))
    handler = logging.FileHandler(log_file_name, encoding='utf-8')
    formatter = logging.Formatter(
        fmt='%(asctime)s|%(module)s|%(funcName)s|%(levelname)s [%(threadName)s id=%(thread)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger():
    d = datetime.now()
    if log_date is None or d.strftime('%Y%m%d') != log_date.strftime('%Y%m%d'):
        create_logger()
    return logging.getLogger(name)
