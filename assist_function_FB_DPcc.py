from typing import Literal

from common_read_and_write_functions import this_is_write_error, write_holding_register, write_holding_registers
from constants_FB_DPcc import CMDOP, CMDOP_REGISTER, PANELSIG, START_VALUE, STATUS1
from func_print_console_and_write_file import print_error, print_text_grey
from read_and_write_functions_FB_DPcc import reset_CmdOp, write_CmdOp
from read_messages import read_new_messages
from read_stutuses_and_message_FB_DPcc import read_PanelSig_one_bit, read_status1_one_bit


def switch_position(command: Literal['MsgOff', 'WHLimEn', 'AHLimEn'],
                    required_bool_value: bool):
    '''!!!! Командой на CmdOp !!!!!'''
    reset_CmdOp()
    if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])
        if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
            print_error(f'Ошибка выполнения команды {command} на СmdOp')


def turn_on_mode(mode: Literal['Oos', 'Imt2', 'Imt1', 'Imt0', 'Fld', 'Tst']):
    '''
    Включает необходимый режим если он еще не включен:\n
    'Oos' - Маскирование, 'Fld' - Полевая обработка, 'Tst' - Тестирование,\n
    'Imt2' - Имитация 1, 'Imt1' - Имитация 1, 'Imt0' - Имитация 0.\n
    !!!!! Возвращает False, если включить не удалось. !!!!!
    '''

    # Провереям включен ли уже данный режим и если не включен, то включаем его.
    if read_status1_one_bit(number_bit=STATUS1[mode]) is False:
        write_CmdOp(command=mode)

    # Возвращаем False и сообщение об ощибки, если включить не удалось.
    if read_status1_one_bit(number_bit=STATUS1[mode]) is True:
        return True
    else:
        print_error(f'Ошибка! Не удалось включить режим {mode}. Дальнейшее тестирование нецелесообразно.')
        return False


def check_st1_PanelSig_new_msg(number_bit_st1, number_bit_PanelSig, old_messages):
    new_msg = read_new_messages(old_messages)
    return (read_status1_one_bit(number_bit=number_bit_st1),
            read_PanelSig_one_bit(number_bit=number_bit_PanelSig),
            new_msg)


def check_work_kvitir_on(old_messages, not_error, msg):
    '''Функция для проверки наличия сигнала "Требуется квитирование".'''

    # Получаем значиния бита квитирования Status1, PanelSig и сообщения.
    st1_kvit, PanelSig, new_msg = check_st1_PanelSig_new_msg(
        number_bit_st1=STATUS1['Kvitir'],
        number_bit_PanelSig=PANELSIG['Kvitir'],
        old_messages=old_messages)

    # Проверяем Status1, PanelSig и сообщения на соответствие эталонным.
    if (st1_kvit and PanelSig) is True and new_msg == msg:
        print_text_grey('Проверка установки сигнала "Требуется квитирование" прошла успешно.')
    else:
        not_error = False
        if st1_kvit is False:
            print_error(f'Ошибка в Status1 пришло {st1_kvit}, а ожидалось True')
        if PanelSig is False:
            print_error(f'Ошибка в PanelSig пришло {PanelSig}, а ожидалось True')
        if new_msg != []:
            print_error(f'Ошибка в сообщениях пришло {new_msg}, а ожидалось {msg}')
    return not_error


def check_work_kvitir_off(old_messages, not_error, msg):
    '''Функция для проверки отсутствия сигнала "Требуется квитирование".'''

    # Получаем значиния бита квитирования Status1, PanelSig и сообщения.
    st1_kvit, PanelSig, new_msg = check_st1_PanelSig_new_msg(
        number_bit_st1=STATUS1['Kvitir'],
        number_bit_PanelSig=PANELSIG['Kvitir'],
        old_messages=old_messages)

    # Проверяем Status1, PanelSig и сообщения на соответствие эталонным.
    if (st1_kvit and PanelSig) is False and new_msg == msg:
        print_text_grey('Проверка установки снятия сигнала "Требуется квитирование" прошла успешно.')
    else:
        not_error = False
        if st1_kvit is True:
            print_error(f'Ошибка в Status1 пришло {st1_kvit}, а ожидалось False')
        if PanelSig is True:
            print_error(f'Ошибка в PanelSig пришло {PanelSig}, а ожидалось False')
        if new_msg != []:
            print_error(f'Ошибка в сообщениях пришло {new_msg}, а ожидалось {msg}')
    return not_error


def switch_position_for_legs(required_bool_value: Literal[True, False],
                             command: Literal['Alarm_Off', 'ChFlt', 'ModFlt', 'SensFlt', 'ExtFlt']):
    # Зиписываем в цикле на нужную ножку значение 3 раза попеременно меняя его.
    # Это связано с особенностями перезаписи этих ножек после ребута ПЛК.
    for _ in range(0, 3):
        if this_is_write_error(address=START_VALUE[command]['register'], value=required_bool_value) is True:
            print_error(f'Ошибка записи на ножку {command}')
        required_bool_value = not required_bool_value


# def write_min_max_EV(MinEV=0.0, MaxEV=100.0):
#     '''Записывает значение макс и мин инженерных значений.'''
#     write_holding_registers(address=START_VALUE['MinEV']['register'], values=MinEV)
#     write_holding_registers(address=START_VALUE['MaxEV']['register'], values=MaxEV)
# 
# 
# def check_write_values_all_setpoints():
#     '''
#     Вспомогательная функция, которая проверяет невозможность задачи значений максимальных и минимальных уставок
#     и инженерных значений. Например - max предупредительный порог > max аварийный порог и т.п.
#     Если выставлено недопустимое значение уставки, то оно не должно быть записано, а также должно сформироваться
#     сообщение о невозможности записи такого значения. Функция работает со следующим списком параметров:
#     ['MinEV', 'ALLim', 'WLLim', 'TLLim', 'THLim', 'WHLim', 'AHLim', 'MaxEV']
#     '''
# 
#     # Создаем словарь для проверки со значениями уставок в диапазовне от 4 до 35.
#     data = {
#         '--': {'WHLim': -10,  'AHLim': -5},
#         '-0': {'WHLim': -5,   'AHLim':  0},
#         '0+': {'WHLim':  0,   'AHLim':  5},
#         '++': {'WHLim':  5,   'AHLim':  10},
#     }
# 
#     # Выставляем значения MinEV и MaxEV. Отключаем все уставки. Создаем переменную для отслеживания ошибок.
#     not_error = True
#     write_min_max_EV(MinEV=-35, MaxEV=35)
#     on_or_off_all_setpoint(required_bool_value=False)
# 
#     # Проходим по словарю data циклом, проверяя сработку уставок на каждом варианте значений.
#     for setpoint_scope, dict_setpoint_value in data.items():
#         print_text_white('-----------------------------------------------------------------------')
#         print_text_white(f'Старт проверки записи, при значениях уставок: {setpoint_scope}')
#         print_text_white('-----------------------------------------------------------------------')
# 
#         # Выставляем значения уставок. проверяем записались уставки или нет.
#         for setpoint_name, setpoint_val in dict_setpoint_value.items():
#             write_holding_registers(address=LEGS[setpoint_name]['register'], values=setpoint_val)
#             read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])
#             if read_setpoint_val != setpoint_val:
#                 print_error(f'Ошибка при записи уставок. Записывали {setpoint_val}, а считали {read_setpoint_val}. '
#                             'Дальнейшее тестирование невозможно.')
#                 not_error = False
#                 break
# 
#         # Проверяем работу каждой уставки проходя по циклу.
#         for setpoint_name, setpoint_val in dict_setpoint_value.items():
#             print_text_white('\n-----------------------------------------------------------------------\n')
#             print_text_white(f'Проверка уставки {setpoint_name} на увеличение:')
# 
#             # Пробуем выставить значения уставок сначала нарушая условие наподобии:
#             # 1) min аварийный > min предупредительный,
#             # 2) min аварийный < MinEV. Читаем сообщения.
#             for k in (1, -1):
#                 print_text_white('На уменьшение:') if k == -1 else None
#                 write_setpoint_val = setpoint_val + (7 * k)
#                 old_messages = read_all_messages()
#                 write_holding_registers(address=LEGS[setpoint_name]['register'], values=write_setpoint_val)
# 
#                 # Cмотрим есть ли новые сообщения. Читаем значение с регистра уставки.
#                 msg = read_new_messages(old_messages)
#                 read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])
# 
#                 # Проверяем записалось ли значение и есть ли какие-то сообщения.
#                 if msg == [] and read_setpoint_val == write_setpoint_val:
#                     print_text_grey(f'Проверка пройдена. При {setpoint_name}En=False значение записалось. '
#                                     'Сообщений нет.')
#                 else:
#                     if msg != []:
#                         print_error(f'При {setpoint_name}En=False при записи значения сформировалось сообщение {msg} '
#                                     'хотя не должно было.')
#                         not_error = False
#                     if read_setpoint_val != write_setpoint_val:
#                         print_error(f'При {setpoint_name}En=False значение не записалось, а должно было записаться.')
#                         not_error = False
# 
#                 # Читаем сообщения. Пробуем включить уставку. Читаем в переменную вкл ли она. Читаем значение уставки.
#                 setpoint_command = setpoint_name + 'En'
#                 old_messages = read_all_messages()
#                 write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[setpoint_command]['CmdOp'])
#                 setpoint_on = read_status1_one_bit(number_bit=STATUS1[setpoint_command])
#                 msg = read_new_messages(old_messages)
#                 read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])
# 
#                 # Проверяем что уставка не вкл, значение сброшено к первоначальному и сформировались 2 сообщения.
#                 # !!!!!!!! СООБЩЕНИЯ ДОЛЖНО БЫТЬ 2 - ЗНАЧЕНИЕ УСТАВКИ НЕКОРРЕКТНОЕ, НЕЛЬЗЯ ВКЛЮЧИТЬ УСТАВКУ. !!!!
#                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  НУЖНО ПОДСТАВИТЬ КОДЫ СООБЩЕНИЙ  !!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                 if msg == ['msg1', 'msg2'] and setpoint_on is False and read_setpoint_val == setpoint_val:
#                     print_text_grey(f'Проверка пройдена. Уставка {setpoint_name} не включилась. Значение сброшено '
#                                     'на первоначальное. Сообщения сформированы.')
#                 else:
#                     if msg != ['msg1', 'msg2']:
#                         print_error(f'Ошибка формирования сообщений. Сформированы {msg}, а ожидалось [msg1, msg2]')
#                         not_error = False
#                     if setpoint_on is True:
#                         print_error('Ошибка! Уставка не должна была включиться.')
#                         not_error = False
#                     if read_setpoint_val != setpoint_val:
#                         print_error('Ошибка! Некорректно записанное значение не сброшено '
#                                     'к первоначальному при вкл уставки.')
#                         not_error = False
# 
#                         # Сбрасываем значение уставки на первоначальное, если оно не сбросилось.
#                         write_holding_registers(address=LEGS[setpoint_name]['register'], values=setpoint_val)
# 
#                 # Включаем уставку. Проверяем включилась ли она.
#                 switch_position(command=setpoint_command, required_bool_value=True)
#                 if read_status1_one_bit(number_bit=STATUS1[setpoint_command]) is False:
#                     print_error(f'Ошибка при включении уставки {setpoint_command}. '
#                                 'Дальнейшее тестирование невозможно.')
#                     not_error = False
#                     break
# 
#                 # Читаем сообщения и записываем значение уставки.
#                 old_messages = read_all_messages()
#                 write_holding_registers(address=LEGS[setpoint_name]['register'], values=write_setpoint_val)
# 
#                 # Cмотрим есть ли новые сообщения. Читаем значение с регистра уставки.
#                 msg = read_new_messages(old_messages)
#                 read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])
# 
#                 # Проверяем записалось ли значение и есть ли какие-то сообщения.
#                 # !!!!!!!!!!!!!!!!!!!!!!!! СООБЩЕНИЯ ДОЛЖНО БЫТЬ 1 - ЗНАЧЕНИЕ УСТАВКИ НЕКОРРЕКТНОЕ. !!!!!!!!!!!!!!!!!
#                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  НУЖНО ПОДСТАВИТЬ КОД СООБЩЕНИЯ  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                 if msg == ['msg1'] and read_setpoint_val == setpoint_val:
#                     print_text_grey(f'Проверка пройдена. При {setpoint_name}En=True значение неизменилось. '
#                                     'Сообщение сформировано верно.')
#                 else:
#                     if msg == []:
#                         print_error(f'При {setpoint_name}En=True при записи значения не сформировалось сообщение [msg1] '
#                                     'хотя должно было.')
#                         not_error = False
#                     elif msg != ['msg1']:
#                         print_error(f'При {setpoint_name}En=True при записи значения сформировалось сообщение {msg}, '
#                                     'а должно было - [msg1].')
#                         not_error = False
#                     if read_setpoint_val != setpoint_val:
#                         print_error(f'При {setpoint_name}En=True значение изменилось, хотя не должно было.')
#                         not_error = False
# 
#                 # Отключаем уставку. Проверяем отключилась ли она.
#                 switch_position(command=setpoint_command, required_bool_value=False)
#                 if read_status1_one_bit(number_bit=STATUS1[setpoint_command]) is True:
#                     print_error(f'Ошибка при отключении уставки {setpoint_command}. '
#                                 'Дальнейшее тестирование невозможно.')
#                     not_error = False
#                     break
#     return not_error
# 