# coding=utf-8

"""
Простым программам - простой логировщик.

Вызывай logger = get_simple_logger('my_logger') и логируй.

Логирует в файл log\<имя логировщика>-YYYYMMDD.log.
Формат лога - см. ниже в FORMATTER.
"""

from datetime import datetime
import logging
from os.path import exists, join
from os import mkdir

FORMATTER = logging.Formatter(
    fmt='%(asctime)s|%(module)s|%(funcName)s|%(levelname)s [%(threadName)s id=%(thread)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def get_simple_logger(name: str) -> logging.Logger:
    """
    Возвращает логировщик, который логирует в файл log\<имя логировщика>-YYYYMMDD.log.

    :param name: имя логировщика.
    :return: логировщик.
    """
    if not exists('log'):
        mkdir('log')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Задаем логирование в файл
    log_file_name = join('log', '%s-%s.log' % (name, datetime.now().strftime('%Y%m%d')))
    handler = logging.FileHandler(log_file_name, 'a', 'utf-8')
    handler.setFormatter(FORMATTER)
    logger.addHandler(handler)

    return logger


def update_logger_file(logger: logging.Logger):
    """
    Пересоздает handler-ы логировщика - чтобы он записывал в новый файл.
    Нужно, если начался новый день, и нужно логировать в файл нового дня.

    :param logger: логировщик
    """
    # Удаляем все handler-ы и задаем новый
    for handler in logger.handlers:
        logger.removeHandler(handler)
    log_file_name = join('log', '%s-%s.log' % (logger.name, datetime.now().strftime('%Y%m%d')))
    handler = logging.FileHandler(log_file_name, 'a', 'utf-8')
    handler.setFormatter(FORMATTER)
    logger.addHandler(handler)


if __name__ == '__main__':
    my_logger = get_simple_logger('hr_common')
    my_logger.info('Hi!')
    my_logger.error('Oh my, it is an error!')
    update_logger_file(my_logger)
    my_logger.warning('Hi again!')