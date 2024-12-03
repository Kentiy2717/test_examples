from assist_function import encode_float, decode_float, decode_bits, decode_uint
from constants_FB_AP import STATUS1_REGISTER, PANEL_SIG_REGISTER
from TCP_Client import client


def read_status1_one_bit(number_bit):
    byte = 3 - number_bit // 8                                     # Вычисляем номер байта, где находится искомый бит.
    bit = 7 - number_bit % 8                                       # Вычисляем номер искомого бита.
    result = client.read_holding_registers(STATUS1_REGISTER, 2)    # Читаем status1 и записываем в переменную.
    return decode_bits(result)[byte][bit]                          # Декодируем в биты статус и возвращаем искомый бит.


def read_panelsig_one_bit(number_bit):
    byte = 3 - number_bit // 8                                     # Вычисляем номер байта, где находится искомый бит.
    bit = 7 - number_bit % 8                                       # Вычисляем номер искомого бита.
    result = client.read_holding_registers(PANEL_SIG_REGISTER, 1)  # Читаем status1 и записываем в переменную.
    return decode_bits(result)[byte][bit]                          # Декодируем в биты статус и возвращаем искомый бит.




def read_status1_all(message):
    pass
