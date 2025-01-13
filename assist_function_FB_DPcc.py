from typing import Literal

from common_read_and_write_functions import this_is_write_error, write_holding_register
from constants_FB_DPcc import CMDOP, CMDOP_REGISTER, STATUS1
from func_print_console_and_write_file import print_error, print_text_grey
from read_and_write_functions_FB_DPcc import reset_CmdOp
from read_messages import read_new_messages
from read_stutuses_and_message_FB_DPcc import read_status1_one_bit


def switch_position(command: Literal['Invers', 'MsgOff'],
                    required_bool_value: bool):
    '''!!!! Командой на CmdOp !!!!!'''
    reset_CmdOp()
    if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
        if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
            print_error(f'Ошибка выполнения команды {command} на СmdOp')
