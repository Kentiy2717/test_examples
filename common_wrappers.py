import sys
import datetime
import time

from time import sleep

from pymodbus.client import ModbusTcpClient
from probably_not_used.constants import HOST, PORT, SLEEP_TIME_BETWEEN_OPERATIONS
from func_print_console_and_write_file import (
    print_passed,
    print_text_grey_start,
    print_error,
    print_failed_test,
    write_to_file
)


def writes_func_failed_or_passed(func):
    def wrapper(*args, **kwargs):
        not_error = True
        not_error = func(not_error, *args, **kwargs)
        if not_error:
            print_passed('Проверка пройдена успешно.\n')
        else:
            print_failed_test(f'Проверка провалена ({func.__name__}).')
        return not_error
    return wrapper


def sleep_time_after_operation(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        sleep(SLEEP_TIME_BETWEEN_OPERATIONS)
        return result
    return wrapper


def running_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        dt_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print_text_grey_start(f'Начало проверки ({dt_now})')
        result = func(*args, **kwargs)
        execution_time = round(time.time() - start_time, 3)
        dt_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print_text_grey_start(f'Функция теста закончила свою работу ({dt_now})')
        print_text_grey_start(f'Время выполнения функции {func.__name__} составило {execution_time} секунд\n')
        write_to_file('______________________________________________________')
        write_to_file('______________________________________________________')
        return result
    return wrapper


def connect_and_close_client(func):
    def wrapper(*args, **kwargs):
        client = ModbusTcpClient(host=HOST, port=PORT)
        print_text_grey_start('\n\nПодключение клиента...')
        try:
            if not client.connect():
                raise Exception
        except Exception:
            print_error(f'Соединение с серверном не установлено. {Exception}\n'
                        f'Проверьте работоспособность сервера и '
                        f'параметры подключения в файле constants.py\n\n'
                        f'Дальнейшая работа невозможна. Останавливаю работу программы.\n')
            sys.exit()
        print_text_grey_start('Подключение установлено\n\n')
        result = func(*args, **kwargs)
        print_text_grey_start('\nОстановка клиента...')
        client.close()
        print_text_grey_start('Стоп\n\n')
        return result
    return wrapper
