from typing import Literal
from common_read_and_write_functions import write_holding_register
from common_wrappers import sleep_time_after_operation
from constants_FB_DP import CMDOP, CMDOP_REGISTER


@sleep_time_after_operation
def reset_CmdOp():
    '''Обнуляет CmdOp.'''

    write_holding_register(address=CMDOP_REGISTER, value=0)


@sleep_time_after_operation
def write_CmdOp(command: Literal['Oos', 'Imt1', 'Imt0', 'Fld', 'Tst', 'Invers', 'MsgOff', 'Kvitir']):
    '''Обнуляет CmdOp, а потом записывает значение переданнов в command.'''

    reset_CmdOp()
    write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
