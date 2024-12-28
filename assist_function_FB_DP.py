from typing import Literal

from common_read_and_write_functions import write_holding_register
from constants_FB_DP import CMDOP, CMDOP_REGISTER, STATUS1
from func_print_console_and_write_file import print_error
from read_and_write_functions_FB_DP import reset_CmdOp, write_CmdOp
from read_stutuses_and_message_FB_DP import read_status1_one_bit


def switch_position(command: Literal['Invers', 'MsgOff'],
                    required_bool_value: bool):
    '''!!!! Командой на CmdOp !!!!!'''
    reset_CmdOp()
    if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
        if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
            print_error(f'Ошибка выполнения команды {command} на СmdOp')


def turn_on_mode(mode: Literal['Oos', 'Imt1', 'Imt0', 'Fld', 'Tst']):
    '''
    Включает необходимый режим если он еще не включен:\n
    'Oos' - Маскирование, 'Imt1' - Имитация 1, 'Imt0' - Имитация 0,\n
    'Fld' - Полевая обработка, 'Tst' - Тестирование.\n
    !!!!! Возвращает False, если включить не удалось. !!!!!
    '''

    # Провереям включен ли уже данный режим и если не включен, то включаем его.
    if read_status1_one_bit(number_bit=STATUS1[mode]) is False:
        write_CmdOp(command=mode)

    # Возвращаем False и сообщение об ощибки, если включить не удалось.
    if read_status1_one_bit(number_bit=STATUS1[mode]) is True:
        return True
    else:
        print_error(f'Ошибка! Не удалось включить режим {mode}. Дальнейшее тестирование нецелесообразно.')
        return False
