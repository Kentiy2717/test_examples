from typing import Literal
from common.common_read_and_write_functions import write_holding_register
from common.common_wrappers import sleep_time_after_operation
from FB_VLV.constants_FB_VLV import CMDOP_REGISTER, CMDOP


@sleep_time_after_operation
def reset_CmdOp():
    '''Обнуляет CmdOp.'''

    write_holding_register(address=CMDOP_REGISTER, value=0)


@sleep_time_after_operation
def write_CmdOp(
    command: Literal['Oos', 'Imt2', 'Imt1', 'Imt0', 'Fld', 'Tst', 'MsgOff', 'WHLimEn', 'AHLimEn', 'Kvitir']
):
    '''Обнуляет CmdOp, а потом записывает значение переданнов в command.'''

    reset_CmdOp()
    if type(command) is str:
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
    else:
        write_holding_register(address=CMDOP_REGISTER, value=command)
