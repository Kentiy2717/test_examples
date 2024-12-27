from typing import Literal

from common_read_and_write_functions import write_holding_register
from constants_FB_DP import CMDOP, CMDOP_REGISTER, STATUS1
from func_print_console_and_write_file import print_error
from read_and_write_functions_FB_DP import reset_CmdOp
from read_stutuses_and_message_FB_DP import read_status1_one_bit


def switch_position(command: Literal['Invers', 'MsgOff'],
                    required_bool_value: bool):
    '''!!!! Командой на CmdOp !!!!!'''
    reset_CmdOp()
    if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
        if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
            print_error(f'Ошибка выполнения команды {command} на СmdOp')
