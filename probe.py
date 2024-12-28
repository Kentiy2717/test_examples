import threading
from time import sleep

from probably_not_used.TCP_Client import connect_client, close_client, client
from encode_and_decode import (encode_float,
                             decode_float,
                             encode_int,
                             decode_int,
                             decoder_bits,
                             )
from read_and_write_functions_FB_DP import write_CmdOp
from read_messages import read_all_messages, read_new_messages
from wrappers_FB_AP import reset_initial_values
# sleep(5)
from common_read_and_write_functions import (
    read_discrete_inputs,
    read_int,
    write_holding_registers,
    write_holding_register,
    read_holding_registers,
    this_is_write_error,
    read_coils,
    write_coil,
    read_float
)
from read_stutuses_and_message_FB_AP import (
    read_PanelSig_one_bit,
    read_status1_one_bit,
    read_PanelMode,
    read_PanelState,
    read_PanelAlm_one_bit,
    read_status2_one_bit
)
from constants_FB_DP import (
    INPUT_REGISTER,
    OUT_REGISTER,
    PANEL_STATE_REGISTER,
    STATUS1
)
from assist_function_FB_AP import switch_position, reset_CmdOp, switch_position_for_legs, turn_on_mode
connect_client()
Out=True
print(read_holding_registers(address=PANEL_STATE_REGISTER, count=1).registers)
print(read_holding_registers(address=PANEL_STATE_REGISTER, count=1).registers[0])
Out1=Out
print(Out1, Out)
Out=False
print(Out1, Out)

close_client()
