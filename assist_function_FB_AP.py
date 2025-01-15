from typing import Literal

from constants_FB_AP import (
    OUTMA_REGISTER,
    PANELSIG,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
    SWITCHES_ST1_PANSIG_MESSAGE as SWITCH,
    STATUS1,
    START_VALUE,
    OUT_REGISTER
)
from read_and_write_functions_FB_AP import reset_CmdOp, write_CmdOp
from read_messages import read_all_messages, read_new_messages
from read_stutuses_and_message_FB_AP import (
    read_PanelSig_one_bit,
    read_status1_one_bit,
)
from common_read_and_write_functions import (
    read_float,
    write_holding_register,
    write_holding_registers,
    read_holding_registers,
    this_is_write_error
)
from func_print_console_and_write_file import (
    print_text_white,
    print_error,
    print_text_grey,
)
from encode_and_decode import decode_float


def set_value_setpoint(name_param: Literal['AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim'],
                       value_of_input: float
                       ):
    '''
    Устанавливает значение уставки в значение равное value_of_input в Input.
    Т.е. если при записи Input 12 -> Out меняется на 50, то
    при value_of_input = 12 и name = 'AHLim' в параметр AHLim установится равным 50-ти.
    '''
    # Запоминаем исходное значение в Input и записываем новое.
    Input = read_float(address=LEGS['Input']['register'])
    write_holding_registers(address=LEGS['Input']['register'], values=value_of_input)

    # Считываем значение полученное в Out и записываем это значение в уставку.
    value_for_name = read_float(address=OUT_REGISTER)
    write_holding_registers(address=LEGS[name_param]['register'], values=value_for_name)

    # Меняем значение в Input на первоначальное и возвращаем записанное значение уставки.
    write_holding_registers(address=LEGS['Input']['register'], values=Input)
    return value_for_name


def set_value_param(name_param: Literal['SpeedLim', 'Hyst', 'DeltaV'],
                    number_units_of_input: float
                    ):
    '''
    Устанавливает значение необходимого параметра в значение равное number_units_of_input единиц
    от Input. Т.е. если при увеличении Input на 1 -> Out меняется с 40 на 50, то
    при number_units_of_input = 1 и name = 'SpeedLim' в параметр SpeedLim установится 10 (50-40).
    '''
    Out1 = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))
    write_holding_registers(address=LEGS['Input']['register'], values=(Input + number_units_of_input))
    Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    value_for_name = Out - Out1
    write_holding_registers(address=LEGS[name_param]['register'], values=value_for_name)
    write_holding_registers(address=LEGS['Input']['register'], values=Input)
    return value_for_name


def on_or_off_all_setpoint(required_bool_value=True):
    '''Выставляем значение всех уставок в положение required_bool_value через CmdOp'''
    for command in ['ALLimEn', 'WLLimEn', 'TLLimEn', 'THLimEn', 'WHLimEn', 'AHLimEn']:
        switch_position(command=command, required_bool_value=required_bool_value)


# def switch_position(command: Literal['AHLimEn', 'WHLimEn', 'THLimEn', 'TLLimEn', 'WLLimEn', 'ALLimEn'],
#                     required_bool_value: bool):
#     '''!!!! Командой на CmdOp !!!!!'''
#     reset_CmdOp()
#     if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
#         write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[command]['CmdOp'])
#         if read_status1_one_bit(STATUS1[command]) is not required_bool_value:
#             print_error(f'Ошибка выполнения команды {command} на СmdOp')


def switch_position(command: Literal['AHLimEn', 'WHLimEn', 'THLimEn', 'TLLimEn', 'WLLimEn', 'ALLimEn'],
                    required_bool_value: bool):
    '''!!!! Командой на CmdOp !!!!!'''
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
        setpoint: Literal['AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim'],
        mode: Literal['Fld', 'Imit', 'Tst'] = 'Fld'):
    '''
    Устанавливает значение аналогового параматра путем подбора значений передаваемых в Input c шагом 1.
    Записывает и возвращает значение Input. Если нужно значение Input, чтобы при пересчете Out > AHLim,
    передаем при вызове функции - set_value_AP(sign='>', setpoint='AHLim').
    '''
    Lim_val = read_float(address=LEGS[setpoint]['register'])                                                           # Получаем значение уставки.
    Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    Input_register = LEGS['Input']['register'] if mode != 'Imit' else LEGS['ImitInput']['register']
    Input = decode_float(read_holding_registers(address=Input_register, count=2))
    if sign == '>':
        while Lim_val >= Out:
            Input += 1
            write_holding_registers(address=Input_register, values=Input)
            Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    elif sign == '<':
        while Lim_val <= Out:
            Input -= 1
            write_holding_registers(address=Input_register, values=Input)                                      # Записываем значение в Input больше на 1.
            Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    Input = decode_float(read_holding_registers(address=Input_register, count=2))
    return Input


def write_min_max_EV(MinEV=0.0, MaxEV=100.0, skip_error=False):
    '''Записывает значение макс и мин инженерных значений.'''
    write_holding_registers(address=LEGS['MinEV']['register'], values=MinEV, skip_error=skip_error)
    write_holding_registers(address=LEGS['MaxEV']['register'], values=MaxEV, skip_error=skip_error)


def check_write_values_all_setpoints():
    '''
    Вспомогательная функция, которая проверяет невозможность задачи значений максимальных и минимальных уставок
    и инженерных значений. Например - max предупредительный порог > max аварийный порог и т.п.
    Если выставлено недопустимое значение уставки, то оно не должно быть записано, а также должно сформироваться
    сообщение о невозможности записи такого значения. Функция работает со следующим списком параметров:
    ['MinEV', 'ALLim', 'WLLim', 'TLLim', 'THLim', 'WHLim', 'AHLim', 'MaxEV']
    '''

    # Создаем словарь для проверки со значениями уставок в диапазовне от -35 до 35.
    data = {
        '------': {'ALLim': -30,  'WLLim': -25,  'TLLim': -20, 'THLim': -15,  'WHLim': -10,  'AHLim': -5},
        '-----0': {'ALLim': -25,  'WLLim': -20,  'TLLim': -15, 'THLim': -10,  'WHLim': -5,   'AHLim':  0},
        '----0+': {'ALLim': -20,  'WLLim': -15,  'TLLim': -10, 'THLim': -5,   'WHLim':  0,   'AHLim':  5},
        '---0++': {'ALLim': -15,  'WLLim': -10,  'TLLim': -5,  'THLim':  0,   'WHLim':  5,   'AHLim':  10},
        '--0+++': {'ALLim': -10,  'WLLim': -5,   'TLLim':  0,  'THLim':  5,   'WHLim':  10,  'AHLim':  15},
        '-0++++': {'ALLim': -5,   'WLLim':  0,   'TLLim':  5,  'THLim':  10,  'WHLim':  15,  'AHLim':  20},
        '0+++++': {'ALLim':  0,   'WLLim':  5,   'TLLim':  10, 'THLim':  15,  'WHLim':  20,  'AHLim':  25},
        '++++++': {'ALLim':  5,   'WLLim':  10,  'TLLim':  15, 'THLim':  20,  'WHLim':  25,  'AHLim':  30},
    }

    # Выставляем значения MinEV и MaxEV. Отключаем все уставки. Создаем переменную для отслеживания ошибок.
    not_error = True
    write_min_max_EV(MinEV=-35, MaxEV=35)
    on_or_off_all_setpoint(required_bool_value=False)

    # Проходим по словарю data циклом, проверяя сработку уставок на каждом варианте значений.
    for setpoint_scope, dict_setpoint_value in data.items():
        print_text_white('-----------------------------------------------------------------------')
        print_text_white(f'Старт проверки записи, при значениях уставок: {setpoint_scope}')
        print_text_white('-----------------------------------------------------------------------')

        # Выставляем значения уставок. проверяем записались уставки или нет.
        for setpoint_name, setpoint_val in dict_setpoint_value.items():
            write_holding_registers(address=LEGS[setpoint_name]['register'], values=setpoint_val)
            read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])
            if read_setpoint_val != setpoint_val:
                print_error(f'Ошибка при записи уставок. Записывали {setpoint_val}, а считали {read_setpoint_val}. '
                            'Дальнейшее тестирование невозможно.')
                not_error = False
                break

        # Проверяем работу каждой уставки проходя по циклу.
        for setpoint_name, setpoint_val in dict_setpoint_value.items():
            print_text_white('\n-----------------------------------------------------------------------\n')
            print_text_white(f'Проверка уставки {setpoint_name} на увеличение:')

            # Пробуем выставить значения уставок сначала нарушая условие наподобии:
            # 1) min аварийный > min предупредительный,
            # 2) min аварийный < MinEV. Читаем сообщения.
            for k in (1, -1):
                print_text_white('На уменьшение:') if k == -1 else None
                write_setpoint_val = setpoint_val + (7 * k)
                old_messages = read_all_messages()
                write_holding_registers(address=LEGS[setpoint_name]['register'], values=write_setpoint_val)

                # Cмотрим есть ли новые сообщения. Читаем значение с регистра уставки.
                msg = read_new_messages(old_messages)
                read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])

                # Проверяем записалось ли значение и есть ли какие-то сообщения.
                if msg == [] and read_setpoint_val == write_setpoint_val:
                    print_text_grey(f'Проверка пройдена. При {setpoint_name}En=False значение записалось. '
                                    'Сообщений нет.')
                else:
                    if msg != []:
                        print_error(f'При {setpoint_name}En=False при записи значения сформировалось сообщение {msg} '
                                    'хотя не должно было.')
                        not_error = False
                    if read_setpoint_val != write_setpoint_val:
                        print_error(f'При {setpoint_name}En=False значение не записалось, а должно было записаться.')
                        not_error = False

                # Читаем сообщения. Пробуем включить уставку. Читаем в переменную вкл ли она. Читаем значение уставки.
                setpoint_command = setpoint_name + 'En'
                old_messages = read_all_messages()
                write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[setpoint_command]['CmdOp'])
                setpoint_on = read_status1_one_bit(number_bit=STATUS1[setpoint_command])
                msg = read_new_messages(old_messages)
                read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])

                # Проверяем что уставка не вкл, значение сброшено к первоначальному и сформировались 2 сообщения.
                # !!!!!!!! СООБЩЕНИЯ ДОЛЖНО БЫТЬ 2 - ЗНАЧЕНИЕ УСТАВКИ НЕКОРРЕКТНОЕ, НЕЛЬЗЯ ВКЛЮЧИТЬ УСТАВКУ. !!!!
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  НУЖНО ПОДСТАВИТЬ КОДЫ СООБЩЕНИЙ  !!!!!!!!!!!!!!!!!!!!!!!!!!!!
                if msg == ['msg1', 'msg2'] and setpoint_on is False and read_setpoint_val == setpoint_val:
                    print_text_grey(f'Проверка пройдена. Уставка {setpoint_name} не включилась. Значение сброшено '
                                    'на первоначальное. Сообщения сформированы.')
                else:
                    if msg != ['msg1', 'msg2']:
                        print_error(f'Ошибка формирования сообщений. Сформированы {msg}, а ожидалось [msg1, msg2]')
                        not_error = False
                    if setpoint_on is True:
                        print_error('Ошибка! Уставка не должна была включиться.')
                        not_error = False
                    if read_setpoint_val != setpoint_val:
                        print_error('Ошибка! Некорректно записанное значение не сброшено '
                                    'к первоначальному при вкл уставки.')
                        not_error = False

                        # Сбрасываем значение уставки на первоначальное, если оно не сбросилось.
                        write_holding_registers(address=LEGS[setpoint_name]['register'], values=setpoint_val)

                # Включаем уставку. Проверяем включилась ли она.
                switch_position(command=setpoint_command, required_bool_value=True)
                if read_status1_one_bit(number_bit=STATUS1[setpoint_command]) is False:
                    print_error(f'Ошибка при включении уставки {setpoint_command}. '
                                'Дальнейшее тестирование невозможно.')
                    not_error = False
                    break

                # Читаем сообщения и записываем значение уставки.
                old_messages = read_all_messages()
                write_holding_registers(address=LEGS[setpoint_name]['register'], values=write_setpoint_val)

                # Cмотрим есть ли новые сообщения. Читаем значение с регистра уставки.
                msg = read_new_messages(old_messages)
                read_setpoint_val = read_float(address=LEGS[setpoint_name]['register'])

                # Проверяем записалось ли значение и есть ли какие-то сообщения.
                # !!!!!!!!!!!!!!!!!!!!!!!! СООБЩЕНИЯ ДОЛЖНО БЫТЬ 1 - ЗНАЧЕНИЕ УСТАВКИ НЕКОРРЕКТНОЕ. !!!!!!!!!!!!!!!!!
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  НУЖНО ПОДСТАВИТЬ КОД СООБЩЕНИЯ  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                if msg == ['msg1'] and read_setpoint_val == setpoint_val:
                    print_text_grey(f'Проверка пройдена. При {setpoint_name}En=True значение неизменилось. '
                                    'Сообщение сформировано верно.')
                else:
                    if msg == []:
                        print_error(f'При {setpoint_name}En=True при записи значения не сформировалось сообщение [msg1] '
                                    'хотя должно было.')
                        not_error = False
                    elif msg != ['msg1']:
                        print_error(f'При {setpoint_name}En=True при записи значения сформировалось сообщение {msg}, '
                                    'а должно было - [msg1].')
                        not_error = False
                    if read_setpoint_val != setpoint_val:
                        print_error(f'При {setpoint_name}En=True значение изменилось, хотя не должно было.')
                        not_error = False

                # Отключаем уставку. Проверяем отключилась ли она.
                switch_position(command=setpoint_command, required_bool_value=False)
                if read_status1_one_bit(number_bit=STATUS1[setpoint_command]) is True:
                    print_error(f'Ошибка при отключении уставки {setpoint_command}. '
                                'Дальнейшее тестирование невозможно.')
                    not_error = False
                    break
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
    if st1_kvit is True and PanelSig is True and new_msg == msg:
        print_text_grey('Проверка установки сигнала "Требуется квитирование" прошла успешно.')
    else:
        not_error = False
        if st1_kvit is False:
            print_error(f'Ошибка. При сработки уставки в Status1 пришло {st1_kvit}, а ожидалось True')
        if PanelSig is False:
            print_error(f'Ошибка. При сработки уставки в PanelSig пришло {PanelSig}, а ожидалось True')
        if new_msg != []:
            print_error(f'Ошибка. При сработки уставки в сообщениях пришло {new_msg}, а ожидалось [112]')
    return not_error


def check_work_kvitir_off(old_messages, not_error):
    '''Функция для проверки отсутствия сигнала "Требуется квитирование".'''

    # Получаем значиния бита квитирования Status1, PanelSig и сообщения.
    st1_kvit, PanelSig, new_msg = check_st1_PanelSig_new_msg(
        number_bit_st1=STATUS1['Kvitir'],
        number_bit_PanelSig=PANELSIG['Kvitir'],
        old_messages=old_messages)

    # Проверяем Status1, PanelSig и сообщения на соответствие эталонным.
    if st1_kvit is False and PanelSig is False and new_msg == [23100]:
        print_text_grey('Проверка установки снятия сигнала "Требуется квитирование" прошла успешно.')
    else:
        not_error = False
        if st1_kvit is True:
            print_error(f'Ошибка. При сработки уставки в Status1 пришло {st1_kvit}, а ожидалось False')
        if PanelSig is True:
            print_error(f'Ошибка. При сработки уставки в PanelSig пришло {PanelSig}, а ожидалось False')
        if new_msg != []:
            print_error(f'Ошибка. При сработки уставки в сообщениях пришло {new_msg}, а ожидалось [23100]')
    return not_error


def turn_on_mode(mode: Literal['Oos', 'Imit', 'Fld', 'Tst'], not_error):
    '''
    Включает необходимый режим если он еще не включен:\n
    'Oos' - Маскирование, 'Imit' - Имитация,\n
    'Fld' - Полевая обработка, 'Tst' - Тестирование.\n
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


def values_out_when_turn_on_simulation_mode(mode: Literal['Oos', 'Imit', 'Fld', 'Tst'], not_error):
    '''
    Функция для проверки переключения значения АП при включении режима "Имитация" из остальных режимов.
    Пользоваться этой функцией нужно только при использовании декоратора reset_initial_values на основной функции.
    '''

    # Включаем режим переданный в параметре "mode".
    not_error = turn_on_mode(mode=mode)

    # Читаем значение в Out и OutmA. Включаем режим "Имитация". Читаем Out'ы еще раз.
    Out_before = read_float(address=OUT_REGISTER)
    OutmA_before = read_float(address=OUTMA_REGISTER)
    not_error = turn_on_mode(mode='Imit')
    Out_after = round(read_float(address=OUT_REGISTER), 1)
    OutmA_after = read_float(address=OUTMA_REGISTER)
    start_ImitInput = START_VALUE['ImitInput']['start_value']

    # Провеяем изменились ли значения в Out и OutmA.
    if Out_before != Out_after and Out_after == start_ImitInput and OutmA_before == OutmA_after:
        print_text_grey('Проверка переключения значения АП при '
                        f'включении режима "Имитация" из режима {mode} пройдена.')
    else:
        not_error = False
        print_error('Ошибка! Проверка переключения значения АП при включении '
                    f'режима "Имитация" из режима {mode} провалена:')
        if Out_before == Out_after:
            print_error(f' - Значение в Out не изменилось, а должно было. Out в режиме {mode} равен {Out_before}.\n'
                        f'   После включения режима "Имитация" также равен {Out_after}.\n'
                        f'   Значение имитации (ImitInput) равно {start_ImitInput}\n')
        if Out_after != start_ImitInput:
            print_error(' - Значение ImitInput записалось не верно или пеерключение идет с искажением.\n'
                        f'   Значение имитации записывалось - ImitInput={start_ImitInput}.\n'
                        f'   Значение Out после включения режима "Имитация" равен {Out_after}\n')
        if OutmA_before != OutmA_after:
            print_error(f' - Значение в OutmA изменилось, а не должно было.\n'
                        f'   OutmA в режиме {mode} равен {OutmA_before}.\n'
                        f'   После включения режима "Имитация" равен {OutmA_after}.')

    # Включаем режим переданный в параметре "mode". Читаем Out'ы еще раз.
    if turn_on_mode(mode=mode) is False:
        not_error = False
        print_error(f'Ошибка! Не удалось включить режим {mode}. Дальнейшее тестирование нецелесообразно.')
    Out_after = read_float(address=OUT_REGISTER)
    OutmA_after = read_float(address=OUTMA_REGISTER)
    if Out_before == Out_after and OutmA_before == OutmA_after:
        print_text_grey('Проверка переключения значения АП при '
                        f'смене режима "Имитация" на режим {mode} пройдена.')
    else:
        not_error = False
        print_error('Ошибка! Проверка переключения значения АП при '
                    f'смене режима "Имитация" на режим {mode} провалена:')
        if Out_before != Out_after:
            print_error(f' - Значение в Out не вернулось к исходному. Out после смены режима равен {Out_after}, '
                        f'а должен быть {Out_before}.')
        if OutmA_before != OutmA_after:
            print_error(f' - Значение в OutmA изменилось, а не должно было.\n'
                        f'   OutmA в режиме "Имитация" равен {OutmA_before}.\n'
                        f'   После включения режима {mode} равен {OutmA_after}.')
    return not_error
