from time import sleep
from probably_not_used.constants import DETAIL_REPORT_ON
from encode_and_decode import decode_float
from func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from common_read_and_write_functions import (
    read_discrete_inputs,
    this_is_write_error,
    write_holding_register,
    write_holding_registers,
    read_holding_registers,
    read_float
)
from read_messages import read_all_messages, read_new_messages
from read_stutuses_and_message_FB_AP import (
    read_PanelAlm_one_bit,
    read_status1_one_bit,
    read_status2_one_bit,
    read_PanelSig_one_bit,
    read_PanelMode,
    read_PanelState
)
from common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from wrappers_FB_DP import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка работы переключателей (командой на CmdOp).')



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
    checking_()

    print('ОБЩИЕ ПРОВЕРКИ\n')
    checking_()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')
    checking_()

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    checking_()


if __name__ == "__main__":
    main()