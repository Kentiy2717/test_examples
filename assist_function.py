from time import sleep
from typing import Literal


from constants_FB_AP import (
    LIST_LIMIT_VALUE_MID_LEVEL,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
    SWITCHES_ST1_PANSIG_MESSAGE as SWITCH,
    STATUS1,
    START_VALUE,
    REGISTERS_FOR_CHECK_STATUS,
    OUT_REGISTER
)
from probably_not_used.constants import SLEEP_TIME_FOR_READ_MESSAGE
from read_stutuses_and_message import (
    read_status1_one_bit,
)
from read_and_write_functions import (
    reset_CmdOp,
    read_float,
    read_coils,
    write_holding_register,
    write_holding_registers,
    read_holding_registers,
    this_is_write_error
)
from func_print_console_and_write_file import (
    print_title,
    print_error,
    print_passed,
    print_text_grey,
    print_failed_test
)
from encode_and_decode import decode_float


def switch_position(command: str, required_bool_value: bool):
    reset_CmdOp()
    if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
        write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[command]['CmdOp'])        
        if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
            print_error(f'Ошибка выполнения команды {command} на СmdOp')


def switch_position_for_legs(required_bool_value: Literal[True, False],
                             command: Literal['AlarmOff', 'ChFlt', 'ModFlt', 'SensFlt', 'ExtFlt',
                                              'ALLimEn', 'WLLimEn', 'TLLimEn', 'THLimEn', 'WHLimEn', 'AHLimEn']):
    # Зиписываем в цикле на нужную ножку значение 3 раза попеременно меняя его.
    # Это связано с особенностями перезаписи этих ножек после ребута ПЛК.
    for _ in range(0, 3):
        if this_is_write_error(address=START_VALUE[command]['register'], value=required_bool_value) is True:
            print_error(f'Ошибка записи на ножку {command}')
        required_bool_value = not required_bool_value


def compare_out_and_setpoint(
        sign: Literal['>', '<', '=', '>=', '<='],
        setpoint: Literal['AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim']
        ):
    out_value = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    setpoint_value = decode_float(read_holding_registers(address=LEGS[setpoint]['register'], count=2))
    if sign == '>':
        result = out_value > setpoint_value
    elif sign == '<':
        result = out_value < setpoint_value
    elif sign == '=':
        result = out_value = setpoint_value
    elif sign == '>=':
        result = out_value >= setpoint_value
    elif sign == '<=':
        result = out_value <= setpoint_value
    return result


def set_value_AP(
        sign: Literal['>', '<'],
        setpoint: Literal['AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim']
        ):
    '''
    Устанавливает значение аналогового параматра путем подбора значений передаваемых в Input c шагом 1.
    Записывает и возвращает значение Input. Если нужно значение Input, чтобы при пересчете Out > AHLim,
    передаем при вызове функции - set_value_AP(sign='>', setpoint='AHLim').
    '''
    Lim_val = read_float(address=LEGS[setpoint]['register'])                                                           # Получаем значение уставки.
    Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    if sign == '>':
        while Lim_val > Out:                                                                                              # Устанавливаем значение Out выше уставки.
            Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))                        # Получаем значение в Input.
            write_holding_registers(address=LEGS['Input']['register'], values=Input+1)                                      # Записываем значение в Input больше на 1.
            Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    if sign == '<':
        while Lim_val < Out:                                                                                              # Устанавливаем значение Out выше уставки.
            Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))                        # Получаем значение в Input.
            write_holding_registers(address=LEGS['Input']['register'], values=Input-1)                                      # Записываем значение в Input больше на 1.
            Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))
    return Input



# def setup_limit_value():
#     '''
#     Функция для установки предельных значений аналогового параметра - уставок(setup_limit_value).
#     Выполняется перед тестами в которых необходимы заданные уставки.
# 
#     Описание:
#         Установка предельных значений осуществляется путем записи регистров среднего уровня.
#         Уставки можно изменить путем редактирования констат в файле(constants_FB_AP.py).
# 
#     Параметры:
#         # Средний уровень.
#         LOWER_LIMIT_VALUE_MID_LEVEL    # нижний предел измерений
#         MIN_ALARM_VALUE_MID_LEVEL      # минимальное аварийное значение
#         MIN_PREALARM_VALUE_MID_LEVEL   # минимальное предельное значение
#         MIN_NORMATIVE_VALUE_MID_LEVEL  # минимальное нормативное значение
#         MAX_NORMATIVE_VALUE_MID_LEVEL  # максимальное нормативное значение
#         MAX_PREALARM_VALUE_MID_LEVEL   # максимальное предельное значение
#         MAX_ALARM_VALUE_MID_LEVEL      # максимальное аварийное значение
#         UPPER_LIMIT_VALUE_MID_LEVEL    # верхний предел измерений
# 
#     Принцип работы:
#         1. Проходим циклом по списку с заданными параметрами уставок (LIST_LIMIT_VALUE_MID_LEVEL).
#         2. Записываем данные(limit_value[1]) в регистр (limit_value[0]) и проверяем записанные данные.
#         3. В случае возникновения ошибки при записи:
#            a. Выводим ошибку.
#            b. Останавливаем работу программы.
#     '''
# 
#     for limit_value in LIST_LIMIT_VALUE_MID_LEVEL:
#         if client.write_register(limit_value[0], limit_value[1]).isError in True:
#             print(f'Ошибка записи уставок в регистр {limit_value[0]}')
#             sys.exit()
# 
# 
# def check_status():
#     '''
#     Функция для чтения и записи в список статусов аналогового параметра со всех регистров(check_status).
# 
#     Описание:
#         Функция создает пустой список и записывает в него значения статусов аналогового параметра проходя циклом
#         по всем регистрам из списка регисров статусов(REGISTERS_FOR_CHECK_STATUS).
# 
#     Параметры:
#         REGISTERS_FOR_CHECK_STATUS: список регистров для проверки статуса аналогового параметра.
# 
#     Принцип работы:
#         1. Создаем пустой список для записи статусов аналогового параметра.
#         2. Проходимся циклом по списку регистров.
#         3. Считываем статус и записываем в список.
#         4. Возвращаем список статусов аналогового параметра.
# 
#     '''
# 
#     list_status = []
#     for register in REGISTERS_FOR_CHECK_STATUS:
#         status = client.read_holding_registers(register, 1).registers[0]  # ???
#         list_status.append(status)
#     return list_status
# 
# 
# def working_with_limit_value(limit_value_low_level,
#                              limit_value_mid_level,
#                              num_registr_low_level,
#                              num_registr_mid_level):
#     '''
#     Функция для работы с уставками(working_with_limit_value).
# 
#     Описание:
#         Вспомогательная функция для получения словаря со списками статусов предельного значения аналогого параметра.
#         Изначально создается пустой список(list_statuses) и список с коэффициентами для расчета (coefficients).
#         На нижний уровень последовательно ведется запись различных значений аналогового параметра в цикле:
#             1. Меньше уставки на 2 гистерезиса;
#             2. Меньше уставки на 0.5 гистерезиса;
#             3. Уставка;
#             4. Больше уставки на 0.5 гистерезиса;
#             5. Больше уставки на 2 гистерезиса;
#             6. Больше уставки на 0.5 гистерезиса;
#             7. Уставка;
#             8. Меньше уставки на 0.5 гистерезиса;
#             9. Меньше уставки на 2 гистерезиса;
#         Также на каждой итерации значение со среднего уровня считывается и сравнивается с эталонным,
#         для подтверждения правильности пересчета подаваемых значений.
#         Если пересчет выполнен корректно, то значение статусов(check_status) добавляется в список list_statuses.
#         Если пересчет был произведен некоректно, то в список list_statuses добавляется сообщение об ошибке.
#         После прохождения по циклу, функция возвращает список со статусами - list_statuses.
# 
#     Функция принимает один аргумента:
#         limit_value_low_level - предельное значение (уставка) аналогового параметра для записи на нижний уровень.
#         limit_value_mid_level - предельное значение (уставка) аналогового параметра для сравнения(средний уровень).
#         num_registr_low_level - номер регистра для записи значений на нижний уровень.
#         num_registr_mid_level - номер регистра для чтения значений на средний уровень.
# 
#     Принцип работы:
#         1. Создаем пустой список statuses и список с коэффициентами для расчета (coefficients).
#         2. Проходим по списку coefficients циклом, на каждой итерации выполняя действия, описанные в пуктах a-e.
#             a. Записываем в переменную value_for_write_low_level значение для записи (нижний уровень).
#             b. Записываем в переменную value_for_write_mid_level расчетное эталонное значение(срединий уровень).
#             c. Подаем значение value_for_write_low_level на запись на нижний уровень в регистр num_registr_low_level.
#             d. Сравниваем пересчитанное значение с эталонным(limit_value_mid_level) на среднем уровне.
#             e. Добавляем значение статусов(check_status) в список list_statuses.
#         3. Возвращаем полученный список list_statuses.
#     '''
# 
#     list_statuses = []
#     coefficients = [-2, -0.5, 0, 0.5, 2, 0.5, 0, -0.5, -2]
#     for coefficient in coefficients:
#         value_for_write_low_level = (limit_value_low_level + coefficient * HYSTERESIS_LOW_LEVEL)
#         value_for_write_mid_level = (limit_value_mid_level + coefficient * HYSTERESIS_MID_LEVEL)
#         client.write_register(address=num_registr_low_level, value=value_for_write_low_level)
#         if client.read_holding_registers(address=num_registr_mid_level, count=1) == value_for_write_mid_level:
#             list_statuses.append(check_status())
#         else:
#             list_statuses.append(f'Ошибка пересчета. Коэффициент - {coefficient}')
#     return list_statuses
# 
# 
# 
# 
# 
# 