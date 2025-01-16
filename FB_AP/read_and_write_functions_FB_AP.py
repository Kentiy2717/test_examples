from common.common_read_and_write_functions import write_holding_register
from common.common_wrappers import sleep_time_after_operation
from FB_AP.constants_FB_AP import (
    CMDOP,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
)


@sleep_time_after_operation
def reset_CmdOp():
    '''Обнуляет CmdOp.'''

    write_holding_register(address=LEGS['CmdOp']['register'], value=0)


@sleep_time_after_operation
def write_CmdOp(command=0):
    '''Обнуляет CmdOp, а потом записывает значение переданнов в value.'''

    reset_CmdOp()
    if type(command) is str:
        write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP[command])
    else:
        write_holding_register(address=LEGS['CmdOp']['register'], value=command)
