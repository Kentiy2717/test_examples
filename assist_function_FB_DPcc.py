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


def turn_on_mode(mode: Literal['Oos', 'Imt2', 'Imt1', 'Imt0', 'Fld', 'Tst'], not_error):
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
    if read_status1_one_bit(number_bit=STATUS1[mode]) is False:
        not_error = False
        print_error(f'Ошибка! Не удалось включить режим {mode}. Дальнейшее тестирование нецелесообразно.')
    return not_error


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
