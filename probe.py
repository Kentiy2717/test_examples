import threading
from time import sleep

from probably_not_used.TCP_Client import connect_client, close_client, client
from encode_and_decode import (encode_float,
                             decode_float,
                             encode_int,
                             decode_int,
                             decoder_bits,
                             )
from wrappers import reset_initial_values, running_time
# sleep(5)
from read_and_write_functions import (
    read_discrete_inputs,
    write_holding_registers,
    write_holding_register,
    read_holding_registers,
    this_is_write_error,
    read_coils,
    write_coil,
    read_float
)
from read_stutuses_and_message import (
    read_PanelSig_one_bit,
    read_status1_one_bit,
    read_all_messages,
    read_new_messages,
    read_PanelMode,
    read_PanelState,
    read_PanelAlm_one_bit,
    read_status2_one_bit
)
from constants_FB_AP import (
    INPUT_REGISTER,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
    OUT_REGISTER,
    SPEED_ACT_REGISTER,
    STATUS1
)
from assist_function import switch_position, reset_CmdOp, switch_position_for_legs, turn_on_mode
# connect_client()
# 
# 
# 
# close_client()
from decimal import Decimal
print(100-(20-(987.123))*(100-0)/(20-4))
print(Decimal(100-(20-(987.123))*(100-0)/(20-4)).quantize(Decimal('.0001')))
print(Decimal('100')-(Decimal('20')-(Decimal('987.123')))*(Decimal('100')-Decimal('0'))/(Decimal('20')-Decimal('4')))
