from time import sleep
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

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')

    # checking_()


if __name__ == "__main__":
    main()
