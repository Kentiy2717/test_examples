from FB_DPcc.constants_FB_DPcc import PANEL_ALM_REGISTER, PANEL_MODE_REGISTER, PANEL_SIG_REGISTER, PANEL_STATE_REGISTER, STATUS1_REGISTER, STATUS2_REGISTER
from common.encode_and_decode import decoder_bits
from common.common_read_and_write_functions import (
    write_holding_registers,
    read_holding_registers
)


def read_status1_one_bit(number_bit):

    # Вычисляем номер байта, где находится искомый бит. Вычисляем номер искомого бита.
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8

    # Читаем status1 и записываем в переменную. Декодируем в биты статус и возвращаем искомый бит.
    result = read_holding_registers(address=STATUS1_REGISTER, count=2)
    return decoder_bits(result)[byte][bit]


def read_PanelSig_one_bit(number_bit):

    # Вычисляем номер байта, где находится искомый бит. Вычисляем номер искомого бита.
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8

    # Читаем panelsig и записываем в переменную. Декодируем в биты статус и возвращаем искомый бит.
    result = read_holding_registers(address=PANEL_SIG_REGISTER, count=1)
    return decoder_bits(result)[byte][bit]


def read_PanelMode():
    result = read_holding_registers(address=PANEL_MODE_REGISTER, count=1).registers
    return result[0]


def read_PanelState():
    result = read_holding_registers(address=PANEL_STATE_REGISTER, count=1).registers
    return result[0]


def read_status2_one_bit(number_bit):
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8
    result = read_holding_registers(address=STATUS2_REGISTER, count=2)
    return decoder_bits(result)[byte][bit]


def read_PanelAlm_one_bit(number_bit):
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8
    result = read_holding_registers(address=PANEL_ALM_REGISTER, count=2)
    return decoder_bits(result)[byte][bit]


def read_status1_all():
    result = write_holding_registers(address=STATUS1_REGISTER, count=2)
    return decoder_bits(result)
