HOST = '10.13.106.10'
# HOST = 'localhost'
PORT = 502
SLAVE = 1
SLEEP_TIME_BETWEEN_OPERATIONS = 0.15  # минимум 0.15, иначе пересчет не работает
SLEEP_TIME_FOR_READ_MESSAGE = 0.2     # минимум 0.2, иначе сообщения не успевают сформироваться
START_LIMIT = False                    # Нужно ли задать стартовое значение на все ножки.
START_LIMIT_VALUE = -99999999.9       # Стартовое значение.
DETAIL_REPORT_ON = True


# Константы для test_example
CHECK_VALUE_WRITE_COILS = [True, False,
                           True, False,
                           True, False,
                           True, False,
                           False, True]
CHECK_VALUE_WRITE_REGISTERS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 00]
VALUE_INPUT_REGISTERS = [True, False,
                         True, False,
                         True, False,
                         True, False,
                         True, False]
VALUE_HOLDING_REGISTERS = [65000, 464, 1464, 2464, 3464,
                           4464, 5464, 6464, 7464, 8464]
