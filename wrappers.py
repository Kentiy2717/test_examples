import sys
import datetime
import time

from time import sleep

from pymodbus.client import ModbusTcpClient
from probably_not_used.constants import HOST, PORT, SLEEP_TIME_BETWEEN_OPERATIONS, START_LIMIT, START_LIMIT_VALUE
from func_print_console_and_write_file import (
    print_passed,
    print_text_grey_start,
    print_error,
    print_failed_test,
    write_to_file
)
from constants_FB_AP import START_VALUE



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


def reset_initial_values(func):
    def wrapper(*args, **kwargs):
        from read_and_write_functions import this_is_write_error
        from assist_function import switch_position
        for name, reg_and_val in START_VALUE.items():
            if this_is_write_error(address=reg_and_val['register'], value=reg_and_val['start_value']) is True:
                print_error(f'Ошибка записи на ножку {name}')

            # Если перзаписываем ножки из списка, то необходимо записать сначала False, True, False.
            # Это связано с особенностями перезаписи этих ножек после ребута ПЛК.
            if name in [#'AlarmOff', 'ChFlt', 'ModFlt', 'SensFlt', 'ExtFlt',
                        'ALLimEn', 'WLLimEn', 'TLLimEn', 'THLimEn', 'WHLimEn', 'AHLimEn']:
                this_is_write_error(address=reg_and_val['register'], value=True)
                this_is_write_error(address=reg_and_val['register'], value=False)
        switch_position(command='MsgOff', required_bool_value=False)
        result = func(*args, **kwargs)
        return result
    return wrapper


def start_with_limits_values(func):
    def wrapper(*args, **kwargs):
        from read_and_write_functions import this_is_write_error
        if START_LIMIT is True:
            for name, reg_and_val in START_VALUE.items():
                if this_is_write_error(address=reg_and_val['register'], value=START_LIMIT_VALUE) is True:
                    print_error(f'Ошибка записи на ножку {name}')
        result = func(*args, **kwargs)
        return result
    return wrapper
