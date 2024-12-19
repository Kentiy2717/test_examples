from time import sleep

from probably_not_used.constants import SLEEP_TIME_FOR_READ_MESSAGE

from encode_and_decode import decoder_bits
from constants_FB_AP import (
    STATUS1_REGISTER,
    STATUS2_REGISTER,
    PANEL_SIG_REGISTER,
    PANEL_MODE_REGISTER,
    PANEL_STATE_REGISTER,
    PANEL_ALM_REGISTER,
    MESSAGES_START_REGISTER,
    MESSAGES_STOP_REGISTER
)
sleep(5)
from read_and_write_functions import (
    write_holding_registers,
    write_holding_register,
    read_holding_registers
)


def read_status1_one_bit(number_bit):  # Работает
    byte = 3 - number_bit // 8                                     # Вычисляем номер байта, где находится искомый бит.
    bit = 7 - number_bit % 8                                       # Вычисляем номер искомого бита.
    result = read_holding_registers(address=STATUS1_REGISTER, count=2)          # Читаем status1 и записываем в переменную.
    return decoder_bits(result)[byte][bit]                          # Декодируем в биты статус и возвращаем искомый бит.


def read_PanelSig_one_bit(number_bit):  # Работает
    byte = 3 - number_bit // 8                                     # Вычисляем номер байта, где находится искомый бит.
    bit = 7 - number_bit % 8                                       # Вычисляем номер искомого бита.
    result = read_holding_registers(address=PANEL_SIG_REGISTER, count=1)         # Читаем panelsig и записываем в переменную.
    return decoder_bits(result)[byte][bit]                          # Декодируем в биты статус и возвращаем искомый бит.


def read_PanelMode():  # Работает
    result = read_holding_registers(address=PANEL_MODE_REGISTER, count=1).registers
    return result[0]


def read_PanelState():  # Работает
    result = read_holding_registers(address=PANEL_STATE_REGISTER, count=1).registers
    return result[0]


def read_status2_one_bit(number_bit):  # Работает
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8
    result = read_holding_registers(address=STATUS2_REGISTER, count=2)
    return decoder_bits(result)[byte][bit]


def read_PanelAlm_one_bit(number_bit):  # Работает
    byte = 3 - number_bit // 8
    bit = 7 - number_bit % 8
    result = read_holding_registers(address=PANEL_ALM_REGISTER, count=2)
    return decoder_bits(result)[byte][bit]


def read_status1_all():  # Работает
    result = write_holding_registers(address=STATUS1_REGISTER, count=2)          # Читаем status1 и записываем в переменную.
    return decoder_bits(result)                                     # Декодируем в биты и возвращаем весь статус.


def read_all_messages():  # Работает
    sleep(SLEEP_TIME_FOR_READ_MESSAGE)
    all_messages = []
    for message in range(MESSAGES_START_REGISTER, MESSAGES_STOP_REGISTER, 2):
        all_messages.append(read_holding_registers(address=message, count=2).registers)
    return all_messages


def read_new_messages(old_messages):  # Работает
    '''Возвращает отсортированный список с новыми сообщениями'''
    now_messages = read_all_messages()
    new_messages = []
    for i in range(0, 50):
        if now_messages[i] != old_messages[i]:
            new_messages.append(now_messages[i][0])
    new_messages.sort()
    return new_messages
