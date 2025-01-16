import sys
import os

# Эта строка добавляет путь к корневой директории проекта в sys.path, чтобы Python мог находить модули и пакеты,
# расположенные в этом проекте, независимо от текущей директории запуска скрипта.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itertools import combinations
from time import sleep

from common.constants import DETAIL_REPORT_ON
from common.common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from common.func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from common.common_read_and_write_functions import (
    read_discrete_inputs,
    this_is_write_error,
    write_coil,
    write_holding_register,
    read_float,
    write_holding_registers,
    write_holding_registers_int
)
from common.read_messages import read_all_messages, read_new_messages
from FB_VLV.assist_function_FB_VLV import (
    check_work_kvitir_off,
    check_work_kvitir_on,
    switch_position,
    switch_position_for_legs,
    turn_on_mode
)
from FB_VLV.constants_FB_VLV import (
    AH_ACT,
    BAD_REGISTER,
    CMDOP,
    CMDOP_REGISTER,
    INPUT_REGISTER,
    OUT_REGISTER,
    PANELMODE,
    PANELSIG,
    PANELSTATE,
    START_VALUE,
    STATUS1,
    STATUS2,
    SWITCH,
    VALUE_UNRELIABILITY,
    WH_ACT,
    WORK_MODES
)
from FB_VLV.read_and_write_functions_FB_VLV import write_CmdOp
from FB_VLV.read_stutuses_and_message_FB_VLV import (
    read_PanelAlm_one_bit,
    read_PanelMode,
    read_PanelSig_one_bit,
    read_PanelState,
    read_status1_one_bit,
    read_status2_one_bit
)
from FB_VLV.wrappers_FB_VLV import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
# 
def checking_(not_error):
    print_title('Проверка .')

    
    return not_error


@running_time
# @start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ АП.
    '''

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')

    print('ОБЩИЕ ПРОВЕРКИ\n')


if __name__ == "__main__":
    main()
