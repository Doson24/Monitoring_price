import logging


def init_logger(name=None):
    # создаем logger
    logger = logging.getLogger(f'{name}_logger')
    logger.setLevel(logging.INFO)

    # создаем обработчик
    handler = logging.FileHandler(f'{name}_logs.log')
    handler.setLevel(logging.INFO)

    # создаем форматирование
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # добавляем обработчик к логгеру
    logger.addHandler(handler)

    # выводим информационное сообщение
    # logger.info('Программа успешно запущена')

    return logger


def logger_obj(log):
    def logger_test(func):
        def wrapper(*args):
            try:
                data = func(*args)
            except Exception as ex:
                log.error(f'Function - {func.__name__},{ex}')
                raise ex
            return data

        return wrapper

    return logger_test


if __name__ == '__main__':
    log = init_logger('ozon')


    @logger_obj(log)
    def test(hui):
        hui = hui + 'asd'
        raise Exception('ПУП')


    test(1)
