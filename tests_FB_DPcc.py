from time import sleep
from constants_FB_DPcc import START_VALUE
from probably_not_used.constants import DETAIL_REPORT_ON
from func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from common_read_and_write_functions import (
    read_coils,
    read_discrete_inputs,
    this_is_write_error,
    write_coil,
    write_holding_register,
    read_float,
    write_holding_registers_int
)
from read_messages import read_all_messages, read_new_messages
from common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from wrappers_FB_DPcc import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
# Проверка ошибок при записи c нулевым, отрицательными и положительными значениями.
def checking_errors_writing_registers(not_error):
    print_title('Проверка ошибок при записи c нулевым и положительными значениями')

    # Создаем словарь с регистрами и значениями.
    data = {
        'Input':     {'register': START_VALUE['Input']['register'],       'values': (-4.1, 0.0, 22.0)},
        'DeltaV':    {'register': START_VALUE['DeltaV']['register'],      'values': (-4.1, 0.5, 0.0)},
        'Period':    {'register': START_VALUE['Period']['register'],      'values': (-4,   0,   100)},
        'MaxEV':     {'register': START_VALUE['MaxEV']['register'],       'values': (2.1,  0.0, 99.9, -23.5)},
        'MinEV':     {'register': START_VALUE['MinEV']['register'],       'values': (0.0, -10.1, 9.9, -123.5)},
        'T01':       {'register': START_VALUE['T01']['register'],         'values': (-4,   0,   1000)},
        'AHLim':     {'register': START_VALUE['AHLim']['register'],       'values': (-99.9, 0.0, 89.7)},
        'WHLim':     {'register': START_VALUE['WHLim']['register'],       'values': (-89.9, 0.0, 89.7)},
        'Hyst':      {'register': START_VALUE['Hyst']['register'],        'values': (-4.1, 0.0, 1.5)},
        'Alarm_Off': {'register': START_VALUE['Alarm_Off']['register'],   'values': (True, False)},
        'ChFlt':     {'register': START_VALUE['ChFlt']['register'],       'values': (True, False)},
        'ModFlt':    {'register': START_VALUE['ModFlt']['register'],      'values': (True, False)},
        'SensFlt':   {'register': START_VALUE['SensFlt']['register'],     'values': (True, False)},
        'ExtFlt':    {'register': START_VALUE['ExtFlt']['register'],      'values': (True, False)},
        'WHLimEn':   {'register': START_VALUE['WHLimEn']['register'],     'values': (True, False)},
        'AHLimEn':   {'register': START_VALUE['AHLimEn']['register'],     'values': (True, False)},
        'CmdOp':     {'register': START_VALUE['CmdOp']['register'],       'values': (-4,   0, 4)},
    }
    # Проходимся циклом по всем регистрам и значениям для записии. Создаем переменные для проверки.
    for name, reg_and_vals in data.items():
        register = reg_and_vals['register']
        values = reg_and_vals['values']
        for num in range(0, len(values)):
            value = values[num]
            error = this_is_write_error(address=register, value=value)
            if error:
                print('') if not_error is True else None
                print_error(f'Значение {value} не записалось на ножку {name} с номером регистра {register}')
                not_error = False
            elif not error:
                print_text_grey(f'Успешная запись {value} на ножку {name} с номером регистра {register}')
            else:
                print_error(f'Неизвестная ошибка. Значение {value} ножка {name} регистр {register}')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@running_time
# @start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ АП.
    '''

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')

    print('ОБЩИЕ ПРОВЕРКИ\n')
    checking_errors_writing_registers()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')

    # checking_()


if __name__ == "__main__":
    main()
