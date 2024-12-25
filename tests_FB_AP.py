from itertools import combinations
import threading
from time import sleep
from assist_function_FB_AP import (
    check_work_kvitir_off,
    check_work_kvitir_on,
    check_write_values_all_setpoints,
    on_or_off_all_setpoint,
    set_value_param,
    switch_position,
    switch_position_for_legs,
    compare_out_and_setpoint,
    set_value_AP,
    turn_on_mode,
    values_out_when_turn_on_simulation_mode,
    write_min_max_EV,
    )
from probably_not_used.constants import DETAIL_REPORT_ON
from constants_FB_AP import (
    BAD_REGISTER,
    INPUT_REGISTER,
    PANELSTATE,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
    OUT_REGISTER,
    OUTMA_REGISTER,
    MINEV_REGISTER,
    MAXEV_REGISTER,
    SPEED_ACT_REGISTER,
    START_VALUE,
    STATUS2,
    SWITCHES_CMDOP,
    SWITCHES_ST1_PANSIG_MESSAGE as SWITCH,
    STATUS1,
    CMDOP,
    PANELMODE,
    VALUE_UNRELIABILITY,
    WORK_MODES
)
from encode_and_decode import decode_float
from func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from read_and_write_functions import (
    read_discrete_inputs,
    reset_CmdOp,
    this_is_write_error,
    write_CmdOp,
    write_holding_register,
    write_holding_registers,
    read_holding_registers,
    read_float
)
from read_stutuses_and_message import (
    read_PanelAlm_one_bit,
    read_status1_one_bit,
    read_status2_one_bit,
    read_PanelSig_one_bit,
    read_PanelMode,
    read_PanelState,
    read_all_messages,
    read_new_messages
)
from wrappers_FB_AP import (
    running_time,
    connect_and_close_client,
    start_with_limits_values,
    writes_func_failed_or_passed,
    reset_initial_values
)


@reset_initial_values
@writes_func_failed_or_passed
def checking_errors_writing_registers(not_error):  # Готово.
    print_title('Проверка ошибок при записи с отрицательными, положительными и нулевым значениями.')
    for name, reg_and_vals in LEGS.items():
        register = reg_and_vals['register']
        for num in range(0, len(reg_and_vals['TEST_VALUES'])):
            value = reg_and_vals['TEST_VALUES'][num]
            error = this_is_write_error(address=register, value=value)
            if error:
                print('') if not_error is True else None
                print_error(f'Значение {value} не записалось на ножку {name} с номером регистра {register}')
                not_error = False
            elif not error:
                print_text_grey(f'Успешная запись {value} на ножку {name} с номером регистра {register}')
            else:
                print_error(f'Неизвестная ошибка. Значение {value} ножка {name} регистр {register}')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def cheking_on_off_for_cmdop(not_error):  # Готово.
    print_title('Проверка работы переключателей (командой на CmdOp).')
    for name, description in SWITCHES_CMDOP.items():
        count_error = 0                                                                                                 # Максимально возможное количество ошибок.
        for i in range(0, 4):                                                                                           # Пытаемся переключить каждый выключатель 4 раза (чтобы он остался в первоначальном состоянии).
            Status1_before = read_status1_one_bit(SWITCH[name]['st1'])                                                  # Читаем status1 и запоминаем значение переключателя.
            PanelSig_before = read_PanelSig_one_bit(SWITCH[name]['PSig'])                                               # Читаем panelsig и запоминаем значение переключателя.
            reset_CmdOp()                                                                                               # Обнуляеся перед подачей команды
            write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[name]['CmdOp'])
            if (
                Status1_before == read_status1_one_bit(SWITCH[name]['st1'])                                             # Если видем в статусе и панели, что не поменялось значение, то ошибка
                and PanelSig_before == read_PanelSig_one_bit(SWITCH[name]['PSig'])
            ):
                print_error(f'Команда {name}({description}) не сработала на {i} итерации.')
                not_error = False
                count_error += 1
        print_text_grey(f'Переключатель {name}({description}) работет исправно.') if count_error == 0 else None         # Если все итерации прошли успешно, то выдаем сообщение.
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_generation_messages_and_msg_off(not_error):  # Готово.
    print_title('Проверка включения и отключения режима генерации сообщений (командой на CmdOp).')

    # Убеждаемся, что генерация сообщений и аварийная уставка включены.
    switch_position(command='MsgOff', required_bool_value=False)
    switch_position(command='AHLimEn', required_bool_value=True)

    # Убеждаемся, что значение АП меньше уставки. Если Out >= AHLim, то выводим ошибку.
    if compare_out_and_setpoint(sign='>=', setpoint='AHLim') is True:
        print_error(
            'Тест не может быть выполнен. Проверьте тест №1. Ошибка записи значений в предыдущих тестах.'
        )
        not_error = False
        return not_error

    # Читаем сообщения. Получаем значение уставки.
    old_messages = read_all_messages()
    AHLim_val = read_float(address=LEGS['AHLim']['register'])

    # Устанавливаем значение Out выше уставки (Out > AHLim).
    Input = set_value_AP(sign='>', setpoint='AHLim')

    # Получаем значение MsgOff и AHAct в статус1.
    MsgOff = read_status1_one_bit(SWITCH['MsgOff']['st1'])
    AHAct = read_status1_one_bit(STATUS1['AHAct'])

    # Если уставка сработала и сообщения сформировались, то выводим сообщение и проверяем дальше.
    if AHAct is True and read_new_messages(old_messages) != []:
        print_text_grey(f'Сообщение о превышении аварийной уставки сформировано. При MsgOff={MsgOff}')

        # Снимаем сигнал уставки. Обновляем значение AHLimEn в статус1.
        write_holding_registers(address=LEGS['Input']['register'], values=12)
        AHAct = read_status1_one_bit(STATUS1['AHAct'])

        # Если аварийный сигнал снят, то продолжаем проверку.
        if AHAct is False:

            # Отключаем генерацию сообщений.
            switch_position(command='MsgOff', required_bool_value=True)

            # Получаем значение MsgOff в статус1. Читаем сообщения.
            MsgOff = read_status1_one_bit(SWITCH['MsgOff']['st1'])
            old_messages = read_all_messages()

            # Устанавливаем  значение в Input выше уставки. Получаем значение AHAct из статус1.
            write_holding_registers(address=LEGS['Input']['register'], values=Input)
            AHAct = read_status1_one_bit(STATUS1['AHAct'])

            # Если уставка сработала и сообщение не формируется, то проверка пройдена.
            if AHAct is True and read_new_messages(old_messages) == []:
                print_text_grey(f'Сообщение о превышении аварийной уставки не сформировано. При MsgOff={MsgOff}')
                return not_error
            else:
                Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
                print_error(
                    f'Сообщение о превышении аварийной уставки сформировалось при MsgOn={MsgOff}. '
                    f'Дальнейшие тесты нецелесообразны. (AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
                )
                not_error = False
                return not_error
        else:
            Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
            print_error(
                'Аварийная уставка не снимается. Дальнейшие тесты нецелесообразны. '
                f'(MsgOn={MsgOff}, AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
            )
            not_error = False
            return not_error
    else:
        Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
        print_error(
            'Сообщение о превышении аварийной уставки не формируется. Дальнейшие тесты нецелесообразны. '
            f'(MsgOn={MsgOff}, AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
        )
        not_error = False
        return not_error


@reset_initial_values
@writes_func_failed_or_passed
def cheking_incorrect_command_cmdop(not_error):  # Готово.
    print_title('Проверка формирования кода 20001 при записи некорректной команды на CmdOp.')
    switch_position(command='MsgOff', required_bool_value=False)
    for command in [900, 949, 999]:
        reset_CmdOp()
        old_messages = read_all_messages()                                                                              # Читаем сообщения.
        write_holding_register(address=LEGS['CmdOp']['register'], value=command)                                        # Подаем в цикле несколько некорректных команд на CmdOp.
        new_messages = read_new_messages(old_messages)                                                                  # Читаем новые сообщения.
        if 20001 in new_messages:                                                                                 # Если в сообщениях сформировались сообщения с кодом 20001(Недопустимая команда оператора), то проверка прошла успешно.
            print_text_grey(f'При передачи команды {command} на CmdOp сформирован ожидаемый код сообщения - 20001.')
        else:                                                                                                           # Если пришло сообщение с другим кодом, то ошибка.
            print_error(f'При передачи команды {command} на CmdOp сформирован код сообщения отличный от ожидаемого. '
                        f'message={new_messages}')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def cheking_on_off_AlarmOff(not_error):  # Готово. Возможно требует доработки проверки на все уставки, а не на одну.
    print_title('Проверка работоспособности AlarmOff.')

    # Переключаем AlarmOff=True и включаем верхнюю уставку. Читаем сообщения.
    switch_position_for_legs(command='AlarmOff', required_bool_value=True)
    switch_position_for_legs(command='AHLimEn', required_bool_value=True)
    old_messages = read_all_messages()

    # Подбираем и устанавливаем значение для записи в Input так, чтобы Out > AHLim и записываем его на ножку Input.
    set_value_AP(sign='>', setpoint='AHLim')

    # Читаем значения Out, AHLim, PanelState, значение 14 бита статус1 и проверяем сообщения.
    Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
    AHLim = decode_float(read_holding_registers(address=LEGS['AHLim']['register'], count=2))
    PanelState = read_PanelState()
    st1 = read_status1_one_bit(number_bit=14)
    new_messages = read_new_messages(old_messages)

    # Если значение Out > AHLim, в PanelState=9, st1=True или сообщениях сработала уставка(114), то ошибка.
    if Out > AHLim and PanelState == 9:
        print_error('AlarmOff не работает. При Out > AHLim уставка сработала в PanelState(значение 9)')
        not_error = False
    if Out > AHLim and st1 is True:
        print_error('AlarmOff не работает. При Out > AHLim значение 14 бита статус1 - True')
        not_error = False
    if Out > AHLim and new_messages != []:
        print_error(f'AlarmOff не работает. При Out > AHLim появились новые сообщения - {new_messages}')
        not_error = False
    if not_error is False:
        return not_error

    # Читаем сообщения. Переключаем AlarmOff=False.
    old_messages = read_all_messages()
    switch_position_for_legs(command='AlarmOff', required_bool_value=False)

    #  Читаем значения PanelState, значение 14 бита статус1 и проверяем сообщения.
    PanelState = read_PanelState()
    st1 = read_status1_one_bit(number_bit=14)
    new_messages = read_new_messages(old_messages)

    # Если значение PanelState=9, st1=True или сообщениях сработала уставка(114), то проверка прошла успешно.    if PanelState == 9 and st1 is True and 114 in new_messages:
    print_text_grey('AlarmOff работает.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_operating_modes(not_error):  # Готово.
    print_title('Проверка возможности включения режимов командой на CmdOp.')
    # Создаем словарь для проверки с наименованиями команд режимов и сообщений при переходе на данные режимы.
    data = {
        'Oos':   {'PanelMode': 1,  'messages': [20100]},
        'Imit':  {'PanelMode': 2,  'messages': [2, 51, 20200]},
        'Tst':   {'PanelMode': 4,  'messages': [5, 52, 20500]},
        'Fld':   {'PanelMode': 3,  'messages': [4, 55, 20400]},
        'Imit1': {'PanelMode': 2,  'messages': [2, 54, 20200]},
    }
    Imit1 = 0  # переменная для получения значений при втором проходе Imit1.
    # Перебираем в цикле команды для включения режимов (Oos, Imit, Tst, Fld, Imit).
    for command in ('Oos', 'Imit', 'Tst', 'Fld', 'Imit'):

        # Читаем сообщения, записываем в переменную и сортируем. Подаем команду на запись на ножку CmdOp.
        old_messages = read_all_messages()
        write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP[command])

        # Каждый проход через 'Imit' увеличиваем Imit1 на 1.
        Imit1 += 1 if command == 'Imit' else 0

        # Читаем новые сообщения, status1 и PanelMode.
        new_messages = read_new_messages(old_messages)
        new_messages.sort()
        status1 = read_status1_one_bit(STATUS1[command])
        PanelMode = read_PanelMode()

        # Если это второй проход через 'Imit', то меняем command.
        command = 'Imit1' if Imit1 == 2 else command

        # Проверяем активацию режимов по сообщениям, status1 и PanelMode. Если соответствуют ожидаемым
        # значениям из словаря data, то проверка пройдена.
        if new_messages == data[command]['messages'] and status1 is True and PanelMode == data[command]['PanelMode']:
            print_text_grey(f'Режим {command} успешно активирован. Проверка пройдена.')
        else:
            print_error(f'Ошибка! Режим {command} не активирован. {new_messages}')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_signal_transfer_low_level_on_middle_level(not_error):  # Готово.
    print_title('Проверка прохождения сигнала с нижнего уровня на средний и правильности пересчета.')

    # Проходим циклом и проверяем в разных режимах.
    for mode in ('Oos', 'Tst', 'Fld',):
        turn_on_mode(mode=mode)
        print_text_white(f'\nПроверка в режиме {mode}.')

        # Создаем вспомогательные переменные со значениями для записи (Input) и сравнения (Out и OutmA).
        # ТАК ДОЛЖНО БЫТЬ. ПЕРЕСЧИТЫВАЛ С ПОМОШЬЮ DECIMAL - МОДУЛЬ ДЛЯ ТОЧНЫХ РАСЧЕТОВ.
        Input_list = (-999.9,  -100.1,    0.0,  4.0,  11.95,  20.0,    88.91,   100.0,  555.67,    987.123, 12.0)
        OutmA_list = (-999.9,  -100.1,    0,  4.0,  11.95,    20.0,    88.91,   100.0,    555.67,    987.123, 12.0)
        Out_list = (-6274.375, -650.625, -25,  0,   49.688,   100.0,   530.688,   600,    3447.938,  6144.519, 50)

        # Подаем поочередно значения на запись на ножку Input. Смотрим нет ли ошибок при записи.
        for i in range(0, len(Input_list)):
            error = this_is_write_error(address=LEGS['Input']['register'], value=Input_list[i])

            # Считываем пересчитанные значения Out и OutmA с регистров.
            Out = round(decode_float(read_holding_registers(address=OUT_REGISTER, count=2)), 3)
            OutmA = round(decode_float(read_holding_registers(address=OUTMA_REGISTER, count=2)), 3)

            # Если Out и OutmA пересчитались кореектно (сравниваем с эталонными из словаря), то проверка пройдена
            if Out == Out_list[i] and OutmA == OutmA_list[i]:
                print_text_grey(f'Значение {Input_list[i]} успешно записалось и пересчиталось.')
            elif Out != Out_list[i]:
                print_error(f'Значение {Input_list[i]} пересчиталось некорректно. '
                            f'Out={Out}, а ожидалось {Out_list[i]}.')
                not_error = False
            elif OutmA != OutmA_list[i]:
                print_error(f'Значение {Input_list[i]} пересчиталось некорректно. '
                            f'Out={OutmA}, а ожидалось {OutmA_list[i]}.')
                not_error = False
            elif error is True:
                print_error(f'Ошибка записи значения {Input_list[i]} в Input.')
                not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_write_maxEV_and_minEV(not_error):  # Готово.
    print_title('Проверка возможности записи min/max инженерного значения.')

    # Создаем вспомогательные переменные со значениями для записи (minEV и maxEV).
    minEV_list = [-9999.9, -100.1, -12.0,  -4.0,  11.95,  -555.67,  9876.123,  0.0]
    maxEV_list = [9999.99,  -90.1,  0.0,    4.0,  21.95,   555.67,  9976.123,  100.0]

    # Записываем поочередно значения в регистры для minEV и maxEV. Смотрим наличие ошибок.
    for i in range(0, len(minEV_list)):
        error_minEV = this_is_write_error(address=MINEV_REGISTER, value=minEV_list[i])
        error_maxEV = this_is_write_error(address=MAXEV_REGISTER, value=maxEV_list[i])

        # Считываем значения minEV и maxEV с регистров.
        minEV = round(decode_float(read_holding_registers(address=MINEV_REGISTER, count=2)), 3)
        maxEV = round(decode_float(read_holding_registers(address=MAXEV_REGISTER, count=2)), 3)

        # Если minEV и maxEV записались кореектно (сравниваем с эталонными из списков), то проверка пройдена.
        if minEV == minEV_list[i] and maxEV == maxEV_list[i]:
            print_text_grey(f'Значения minEV={minEV_list[i]} и maxEV={maxEV_list[i]} успешно записались.')
        elif minEV != minEV_list[i]:
            print_error(f'Значение записалось некорректно. minEV={minEV}, а ожидалось {minEV_list[i]}.')
            not_error = False
        elif maxEV != maxEV_list[i]:
            print_error(f'Значение записалось некорректно. minEV={maxEV}, а ожидалось {maxEV_list[i]}.')
            not_error = False
        elif error_minEV is True:
            print_error(f'Ошибка записи min инженерного значения {minEV_list[i]}.')
            not_error = False
        elif error_maxEV is True:
            print_error(f'Ошибка записи max инженерного значения {maxEV_list[i]}.')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_not_impossible_min_ev_more_max_ev(not_error):  # Готово.
    print_title('Проверка невозможности записи minEV > maxEV.')

    # Создаем вспомогательные переменные со значениями для записи, где minEV > maxEV.
    maxEV_list = [-9999.9, -100.1, -12.0,  -4.0,  11.95,  -555.67,  9876.123,  0.0]
    minEV_list = [9999.99,  -90.1,  0.0,    4.0,  21.95,   555.67,  9976.123,  100.0]

    # Записываем поочередно значения в регистры для minEV и maxEV.
    for i in range(0, len(minEV_list)):
        this_is_write_error(address=MINEV_REGISTER, value=minEV_list[i])
        error_maxEV = this_is_write_error(address=MAXEV_REGISTER, value=maxEV_list[i])

        # Считываем значения minEV и maxEV с регистров.
        minEV = round(decode_float(read_holding_registers(address=MINEV_REGISTER, count=2)), 3)
        maxEV = round(decode_float(read_holding_registers(address=MAXEV_REGISTER, count=2)), 3)

        # Если minEV и maxEV записались кореектно (сравниваем с эталонными из списков), то проверка пройдена.
        if minEV == minEV_list[i] and maxEV == maxEV_list[i] and minEV > maxEV:
            print_error(
                f'Ошибочная запись значений! MIN значение({minEV_list[i]}) '
                f'не может быть больше чем MAX({maxEV_list[i]}).'
            )
            not_error = False
        elif minEV < maxEV and error_maxEV is True:
            print_text_grey(f'Тест со значениями minEV={minEV} и maxEV={maxEV} пройден. minEV < maxEV по прежнему.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_errors_channel_module_sensor_and_external_error_fld_and_tst(not_error):  # Готово.
    print_title('Проверка сработки ошибок канала, модуля, сенсора и внешней ошибки.')

    # Создаем словарь с данными для проверки. Ключи - ошибки, знач. списки значений сообщений.
    data = {
        'ChFlt':    {'bit': 0, 'msg_by_True': [204, 212], 'msg_by_False': [111, 254, 262]},
        'ModFlt':   {'bit': 1, 'msg_by_True': [206, 212], 'msg_by_False': [111, 256, 262]},
        'SensFlt':  {'bit': 2, 'msg_by_True': [208, 212], 'msg_by_False': [111, 258, 262]},
        'ExtFlt':   {'bit': 3, 'msg_by_True': [210, 212], 'msg_by_False': [111, 260, 262]}
    }

    # Проверяем в цикле режим "Полевая обработка" и "Тестирование".
    for mode in ('Fld', 'Tst'):
        turn_on_mode(mode=mode)
        print_text_white(f'Режим {mode}.')

        # Проходим по значениям словаря с наименованием ошибок.
        for name, msg in data.items():

            # ПРОВЕРКА ВКЛЮЧЕНИЯ.
            # Читаем сообщения dыбираем какой бит смотреть в status2 и PanelAlm.
            old_message = read_all_messages()
            bit = data[name]['bit']
            #  Переключаем значение ошибки в True. Проверяем что ошибки записи нет.
            if this_is_write_error(address=START_VALUE[name]['register'], value=True) is True:
                print_error(f'Ошибка записи значения False в {name}. Проверьте адрес регистра.')
                not_error = False
                continue

            # Читаем сообщения, создаем счетчик ошибок.
            new_messages = read_new_messages(old_message)
            standart_msg = msg['msg_by_True']
            count_error = 0

            # Если сообщения не совпадают с ожидаемыми, то ошибка.
            if new_messages != standart_msg:
                print_error(f'Ошибка включения {name}! Сообщения не соответствуют ожидаемым.'
                            f'Пришло {new_messages}, а ожидалось {standart_msg}.')
                count_error += 1
            # Если значение битов status1(7), status2(bit), PanelAlm(bit) - False, то ошибка.
            if read_status1_one_bit(7) is False:
                print_error(f'Ошибка включения {name}! 7 бит status1={read_status1_one_bit(7)}.')
                count_error += 1
            if read_status2_one_bit(bit) is False:
                print_error(f'Ошибка включения {name}! {bit} бит status2={read_status2_one_bit(bit)}.')
                count_error += 1
            if read_PanelAlm_one_bit(bit) is False:
                print_error(f'Ошибка включения {name}! {bit} бит PanelAlm={read_PanelAlm_one_bit(bit)}.')
                count_error += 1

            # Если count_error = 0 то проверка прошла успешно, если 4, то полностью провалилась, если 1-3 то частично.
            if count_error == 0:
                print_text_grey(f'Проверка включиния {name} прошла успешно.')
            elif count_error in (1, 2, 3):
                print_text_grey(f'Проверка включиния {name} частично провалена. Подробности выше.')
                not_error = False
            elif count_error == 4:
                print_error(f'Проверка включиния {name} провалена.')
                not_error = False
            else:
                print_error(f'Неизвестная ошибка при проверке включиния {name}. '
                            f'Проверь работу тестов count_error={count_error}.')

            # ПРОВЕРКА ОТКЛЮЧЕНИЯ.
            old_message = read_all_messages()
            # Читаем сообщения. Переключаем значение ошибки в False. Проверяем что ошибки записи нет.
            if this_is_write_error(address=START_VALUE[name]['register'], value=False) is True:
                print_error(f'Ошибка записи значения False в {name}. Проверьте адрес регистра.')
                not_error = False
                continue

            # Читаем сообщения, обнуляем счетчик ошибок.
            new_messages = read_new_messages(old_message)
            standart_msg = msg['msg_by_False']
            count_error = 0

            # Если сообщения не совпадают с ожидаемыми, то ошибка.
            if new_messages != standart_msg:
                print_error(f'Ошибка отключения {name}! Сообщения не соответствуют ожидаемым.'
                            f'Пришло {new_messages}, а ожидалось {standart_msg}.')
                count_error += 1
            # Если значение битов status1(7), status2(0), PanelAlm(0) - False, то ошибка.
            if read_status1_one_bit(7) is True:
                print_error(f'Ошибка отключения {name}! 7 бит status1={read_status1_one_bit(7)}.')
                count_error += 1
            if read_status2_one_bit(bit) is True:
                print_error(f'Ошибка отключения {name}! {bit} бит status2={read_status2_one_bit(bit)}.')
                count_error += 1
            if read_PanelAlm_one_bit(bit) is True:
                print_error(f'Ошибка отключения {name}! {bit} бит PanelAlm={read_PanelAlm_one_bit(bit)}.')
                count_error += 1

            # Если count_error = 0 то проверка прошла успешно, если 4, то полностью провалилась, если 1-3 то частично.
            if count_error == 0:
                print_text_grey(f'Проверка отключения {name} прошла успешно.')
            elif count_error in (1, 2, 3):
                print_text_grey(f'Проверка отключения {name} частично провалена. Подробности выше.')
                not_error = False
            elif count_error == 4:
                print_error(f'Проверка отключения {name} провалена.')
                not_error = False
            else:
                print_error(f'Неизвестная ошибка при проверке отключения {name}. '
                            f'Проверь работу тестов count_error={count_error}.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_messages_on_off_setpoints(not_error):  # Готово.
    print_title('Проверка наличия сообщений при включени и отключении уставок.')

    # Создаем словарь с данными для проверки. Ключи - уставки, значения - списки со значениями кодов в сообщениях.
    data = {
        'ALLimEn': {'st1': 22, 'msg_on': [22, 22200], 'msg_off': [72, 22200]},
        'WLLimEn': {'st1': 23, 'msg_on': [23, 22300], 'msg_off': [73, 22300]},
        'TLLimEn': {'st1': 24, 'msg_on': [24, 22400], 'msg_off': [74, 22400]},
        'THLimEn': {'st1': 25, 'msg_on': [25, 22500], 'msg_off': [75, 22500]},
        'WHLimEn': {'st1': 26, 'msg_on': [26, 22600], 'msg_off': [76, 22600]},
        'AHLimEn': {'st1': 27, 'msg_on': [27, 22700], 'msg_off': [77, 22700]},
    }

    # Проходимся циклом по словарю. И запоминаем нужные переменные.
    for name, param in data.items():
        msg_on = param['msg_on']
        msg_off = param['msg_off']
        bit = param['st1']

        # ПРОВЕРКА ВКЛЮЧЕНИЯ УСТАВКИ.
        # Читаем сообщения, включаем уставку.
        old_message = read_all_messages()
        switch_position(command=name, required_bool_value=True)

        # Проверяем что уставка включена по status1 и новые сообщения на соответствие ожидаемым.
        st1 = read_status1_one_bit(number_bit=bit)
        new_messages = read_new_messages(old_message)
        if st1 is True and new_messages == msg_on:
            print_text_grey(f'Проверка включиния {name} прошла успешно.')
        elif st1 is True and new_messages != msg_on:
            print_error(f'Проверка включиния провалена. Получили {new_messages}, а ожидалось {msg_on}')
            not_error = False
        else:
            print_error(f'Неизвестая ошибка включения. st1={st1}(должен быть True).')
            not_error = False

        # ПРОВЕРКА ОТКЛЮЧЕНИЯ УСТАВКИ.
        # Читаем сообщения, отключаем уставку.
        old_message = read_all_messages()
        switch_position(command=name, required_bool_value=False)

        # Проверяем что уставка включена по status1 и новые сообщения на соответствие ожидаемым.
        st1 = read_status1_one_bit(number_bit=bit)
        new_messages = read_new_messages(old_message)
        if st1 is False and new_messages == msg_off:
            print_text_grey(f'Проверка отключения {name} прошла успешно.')
        elif st1 is False and new_messages != msg_off:
            print_error(f'Проверка отключения провалена. Получили {new_messages}, а ожидалось {msg_off}')
            not_error = False
        else:
            print_error(f'Неизвестая ошибка отключения. st1={st1}(должен быть False).')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_setpoint_values(not_error):  # Готово.
    print_title('Проверка правильности записи значения уставок.')

    # Т.к. значения уставок записывались декоратором reset_initial_values, то
    # необходимо считать соответствующие регисты и сравнить исходные данные со считанными.

    # Проходим циклом по списку с названиями уставок. Записываем в переменные эталонное значение и считанное.
    for name in ['AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim']:
        val = START_VALUE[name]['start_value']
        read_val = read_float(address=START_VALUE[name]['register'])

        # Если значения переменных равны, то данные записались верно.
        if val == read_val:
            print_text_grey(f'Значение уставки {name} записалось верно.')
        else:
            print_error(f'Значение уставки {name} записалось неверно. '
                        f'Эталонное значение - {val}, считанное - {read_val}')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_setpoint_not_impossible_min_more_max(not_error):
    print_title('Проверка логики задачи значений максимальных и минимальных уставок и инженерных значений.\n'
                'Например - max предупредительный порог > max аварийный порог.')

    # Проверяем невозможность выставить недопустимые значения уставок (наподобии max предупредит. > max аварийный).
    not_error = check_write_values_all_setpoints()
    return not_error


@writes_func_failed_or_passed
def checking_DeltaV(not_error):  # Готово.
    print_title('Проверка работы DeltaV при изменение Input.')

    @reset_initial_values
    def checking_DeltaV_one_mode(not_error):
        # Задаем значение DeltaV равное 1 на нижнем уровне. Запоминаем значение в Out.
        Out1 = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
        Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))
        write_holding_registers(address=LEGS['Input']['register'], values=(Input + 1))
        Out = decode_float(read_holding_registers(address=OUT_REGISTER, count=2))
        DeltaV = Out - Out1
        write_holding_registers(address=LEGS['DeltaV']['register'], values=DeltaV)

        # Проверяем правильность записи значения DeltaV.
        if DeltaV == decode_float(read_holding_registers(address=LEGS['DeltaV']['register'], count=2)):
            print_text_grey('DeltaV записывается верно.')
        else:
            print_error('DeltaV записывается не верно.')
            not_error = False

        # Подаем значения в пределах DeltaV (Input +-1 на нижнем уровне).
        for value in [0.5, -0.5, 1, -1, 0]:
            write_holding_registers(address=LEGS['Input']['register'], values=(Input + value))
            # Cмотрим, что значение в Out изменилось.
            if Out != decode_float(read_holding_registers(address=OUT_REGISTER, count=2)) and not_error is False:
                print_error('DeltaV работает не верно при изменении значения Out меньше чем DeltaV')
                not_error = False
        print_text_grey('DeltaV работает верно при изменении значения Out меньше чем DeltaV')

        # Подаем значения больше DeltaV(Input +- > 1 на нижнем уровне).
        for value in [1.001, -1.001]:
            write_holding_registers(address=LEGS['Input']['register'], values=(Input + value))
            # Cмотрим, что значение в Out изменилось.
            if Out == decode_float(read_holding_registers(address=OUT_REGISTER, count=2)):
                print_error('DeltaV работает не верно при изменении значения Out больше чем DeltaV')
                not_error = False
        print_text_grey('DeltaV работает верно при изменении значения Out больше чем DeltaV')

        # Подаем значения меньше DeltaV, но перезаписываем Input, чтобы в сумме получить изменение больше чем DeltaV.
        for value in [0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.001]:
            write_holding_registers(address=LEGS['Input']['register'], values=(Input + value))
            Input = decode_float(read_holding_registers(address=LEGS['Input']['register'], count=2))
        # Cмотрим, что значение в Out изменилось.
        if Out == decode_float(read_holding_registers(address=OUT_REGISTER, count=2)):
            print_error('DeltaV работает не верно при многократном изменении значения Out '
                        'на значение < DeltaV, но в сумме больше чем DeltaV')
            not_error = False
        print_text_grey('DeltaV работает верно при многократном изменении значения Out '
                        'на значение < DeltaV, но в сумме больше чем DeltaV')
        return not_error

    for mode in WORK_MODES:
        turn_on_mode(mode=mode)
        print_text_white(f'Проверка в режиме {mode}.')
        not_error = checking_DeltaV_one_mode(not_error)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка работы SpeedLim в во всех режимах работы.
def checking_SpeedLim(not_error):  # Готово.
    print_title('Проверка работы SpeedLim в разных режимах работы.')

    # Проходим циклом по всем режимам работы, включаем поочередно и тестируем работу SpeedLim.
    for mode in WORK_MODES:
        turn_on_mode(mode=mode)

        # Включаем SpeedLim и задаем значение ниже чем 1 в Input на нижнем уровне.
        switch_position(command='SpeedOff', required_bool_value=True)
        SpeedLim = set_value_param(name_param='SpeedLim', number_units_of_input=1)
        write_holding_registers(address=LEGS['SpeedLim']['register'], values=SpeedLim)

        # Создаем функцию для изменения значений в Input которая будет запускаться в отдельном потоке.
        def change_value(start, stop, step):
            for value in range(start, stop, step):
                write_holding_registers(address=LEGS['Input']['register'], values=value)

        # Вызываем функцию change_value в отдельном потоке с параметрами от 4 до 20 и в обратном направлении.
        for start, stop, step in ((4, 20, 1), (20, 4, -1)):
            thread = threading.Thread(target=change_value, daemon=True, args=(start, stop, step))
            thread.start()

            # Ждем 3 секунды, чтобы статусы успели обновиться  и проверяем 18 бит для status1, 0-й для PanelSig
            # и читаем с ножки SPEED_ACT.
            sleep(2)
            check_st1_and_PanelSig = read_status1_one_bit(STATUS1['SpeedMax']) and read_PanelSig_one_bit(0)
            SpeedAct = read_discrete_inputs(address=SPEED_ACT_REGISTER, bit=0)

            # Пишем условия проверки в зависимости от режима работы.
            Oos_passed = mode == 'Oos' and (SpeedAct and check_st1_and_PanelSig) is False
            Imit_passed = mode == 'Imit' and (SpeedAct and check_st1_and_PanelSig) is False
            Fld_passed = (mode == 'Fld' and SpeedAct and check_st1_and_PanelSig) is True
            Tst_passed = mode == 'Tst' and check_st1_and_PanelSig is True and SpeedAct is False

            # Если оба бита False, то проверка провалилась, если True, то прошла.
            if (Fld_passed or Tst_passed or Oos_passed or Imit_passed) is True:
                print_text_grey(f'Проверка пройдена в режиме "{mode}". При изменении значений от {start} до {stop}. '
                                'SpeedLim работает исправно.')
            else:
                not_error = False
                print_error(f'Проверка провалена в режиме "{mode}". '
                            f'При изменении значений от {start} до {stop}. SpeedLim не работает.')
            sleep(3)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка сработки уставок при режиме во всех режимах работы.
def checking_work_setpoint(not_error):  # !!!!!!!!!!! НАДО ПРОВЕРИТЬ РАБОТУ for k in !!!!!!!!!!!!!!
    print_title('Проверка сработки уставок во всех режимах.')
    print_error('НАДО ПРОВЕРИТЬ РАБОТУ for k in.')
    print()

    # Создаем словарь для проверки. Ключи - уставки, значение - словарь с номером бита (status1),
    # значением для PanelState, сообщениями и регистром ножки для каждой уставки соответственно.
    data = {
        'ALLim': {'st1': 8,  'PanelState': 3, 'leg': 40011, 'k': -1, 'msg_on': ([108], [158]), 'msg_off': ([], [])},
        'WLLim': {'st1': 9,  'PanelState': 4, 'leg': 40010, 'k': -1, 'msg_on': ([109], [159]), 'msg_off': ([], [])},
        'TLLim': {'st1': 10, 'PanelState': 5, 'leg': 40009, 'k': -1, 'msg_on': ([110], [160]), 'msg_off': ([111], [161])},
        'THLim': {'st1': 12, 'PanelState': 7, 'leg': 40008, 'k':  1, 'msg_on': ([112], [162]), 'msg_off': ([111], [161])},
        'WHLim': {'st1': 13, 'PanelState': 8, 'leg': 40007, 'k':  1, 'msg_on': ([113], [163]), 'msg_off': ([], [])},
        'AHLim': {'st1': 14, 'PanelState': 9, 'leg': 40006, 'k':  1, 'msg_on': ([114], [164]), 'msg_off': ([], [])},
    }

    # Включаем все уставки. Устанавливаем значения MaxEV и MinEV - 100 и -100 соответственно.
    on_or_off_all_setpoint()
    write_min_max_EV(MinEV=-100, MaxEV=100)

    # Находим середину диапазона физических значений.
    RangeMax = read_float(address=LEGS['RangeMax']['register'])
    RangeMin = read_float(address=LEGS['RangeMin']['register'])
    mid_range = (RangeMax - RangeMin) / 2 + RangeMin

    # Устанавливаем значение гистерезиса равное 0.2 от Input.
    hyst_mA = 0.2
    hyst = set_value_param(name_param='Hyst', number_units_of_input=hyst_mA)

    # Создаем словарь со значениями уставок, для проверки работы в только отрицательной, только положительной и
    # комбинированных областях их работы.
    dict_setpoint_values = {
        '------': {'ALLim': -30,  'WLLim': -25,  'TLLim': -20, 'THLim': -15,  'WHLim': -10,  'AHLim': -5},
        '-----0': {'ALLim': -25,  'WLLim': -20,  'TLLim': -15, 'THLim': -10,  'WHLim': -5,   'AHLim':  0},
        '----0+': {'ALLim': -20,  'WLLim': -15,  'TLLim': -10, 'THLim': -5,   'WHLim':  0,   'AHLim':  5},
        '---0++': {'ALLim': -15,  'WLLim': -10,  'TLLim': -5,  'THLim':  0,   'WHLim':  5,   'AHLim':  10},
        '--0+++': {'ALLim': -10,  'WLLim': -5,   'TLLim':  0,  'THLim':  5,   'WHLim':  10,  'AHLim':  15},
        '-0++++': {'ALLim': -5,   'WLLim':  0,   'TLLim':  5,  'THLim':  10,  'WHLim':  15,  'AHLim':  20},
        '0+++++': {'ALLim':  0,   'WLLim':  5,   'TLLim':  10, 'THLim':  15,  'WHLim':  20,  'AHLim':  25},
        '++++++': {'ALLim':  5,   'WLLim':  10,  'TLLim':  15, 'THLim':  20,  'WHLim':  25,  'AHLim':  30},
    }

    # Проходимся циклом по кортежу режимов и выполняем проверку уставок в каждом режиме.
    for mode in ('Oos', 'Tst', 'Imit', 'Fld'):
        turn_on_mode(mode=mode)
        print(f'Проверка в режиме {mode}')

        # Проходимся по словарю dict_setpoint_values циклом и проверяем сработку уставок на каждом варианте значений.
        for setpoint_scope, dict_setpoint_value in dict_setpoint_values.items():
            print_text_white('-----------------------------------------------------------------------')
            print_text_white(f'Старт проверки работы уставок, при значениях уставок: {setpoint_scope}')
            print_text_white('-----------------------------------------------------------------------')

            # Выставляем значения уставок.
            for set_name, set_val in dict_setpoint_value.items():
                write_holding_registers(address=LEGS[set_name]['register'], values=set_val*hyst)

            # Проходим циклом по словарю еще раз и проверяем сработку каждой из уставок.
            for set_name, set_val in dict_setpoint_value.items():

                # Устанавливаем значение Input -3 гистерезиса от уставки, для сброса ненужных сообщений.
                if mode == 'Imit':
                    write_holding_registers(
                        address=LEGS['ImitInput']['register'],
                        values=set_val * hyst + (-3 * data[set_name]['k'] * hyst)
                    )
                else:
                    write_holding_registers(
                        address=LEGS['Input']['register'],
                        values=set_val * hyst_mA + (-3 * data[set_name]['k'] * hyst_mA) + mid_range
                    )

                # Подставляем значение коэффициента в формулу расчета знач., подаваемого в Input и проверяем сработку.
                # В Input последовательно ведется запись следующих значений аналогового параметра в цикле:
                #     1. Меньше уставки на 2 гистерезиса - уставка НЕ должна сработать;
                #     2. Меньше уставки на 0.5 гистерезиса - уставка НЕ должна сработать;
                #     3. Уставка - уставка ДОЛЖНА сработать;
                #     4. Больше уставки на 0.5 гистерезиса - уставка ДОЛЖНА сработать;
                #     5. Больше уставки на 2 гистерезиса - уставка ДОЛЖНА сработать;
                #     6. Больше уставки на 0.5 гистерезиса - уставка ДОЛЖНА сработать;
                #     7. Уставка - уставка ДОЛЖНА сработать;
                #     8. Меньше уставки на 0.5 гистерезиса - уставка ДОЛЖНА сработать;
                #     9. Меньше уставки на 2 гистерезиса - уставка НЕ должна сработать;

                # Это как у нас сейчас работает.
                # for k in ((-2, False, ), (-0.5, False), (0, False), (0.5, True, 'msg_on'),
                #           (2, True),     (0.5, True),   (0, True),  (-0.5, True),
                #           (-2, False, 'msg_off')):

                # ЭТО КАК ДОЛЖНО БЫТЬ!
                for k in ([-2, False, ], [-0.5, False], [0, True, 'msg_on'], [0.5, True],
                          [2, True],     [0.5, True],   [0, True],           [-0.5, True],
                          [-2, False, 'msg_off']):

                    # Находим по формуле значение, которое необходимо записать в Input, читаем сообщения и записываем.
                    if mode == 'Imit':
                        Input = set_val * hyst + (data[set_name]['k'] * k[0] * hyst)
                        Input_leg = LEGS['ImitInput']['register']
                    else:
                        Input = set_val * hyst_mA + (data[set_name]['k'] * k[0] * hyst_mA) + mid_range
                        Input_leg = LEGS['Input']['register']
                    old_messages = read_all_messages()
                    write_holding_registers(address=Input_leg, values=Input)

                    # Читаем значения status1, PanelState, с ножки, сообщения и сравниваем с эталоном из data.
                    number_bit_st1 = data[set_name]['st1']
                    PanelState_val = data[set_name]['PanelState']
                    leg_register = data[set_name]['leg']
                    st1 = read_status1_one_bit(number_bit=number_bit_st1)
                    PanelState = read_PanelState()
                    leg = read_discrete_inputs(address=leg_register, count=1, bit=0)
                    msg = read_new_messages(old_messages)

                    # Изменяем k[1] (сработка на ножках), если режим Tst.
                    leg_k1 = False if mode == 'Tst' else k[1]

                    # Проверяем правильно ли сформировались сообщения и код в PanelState.
                    if len(k) == 3:
                        if mode != 'Imit':
                            expected_msg = data[set_name][k[2]][0]
                        else:
                            expected_msg = data[set_name][k[2]][1]
                        msg_passed = msg == expected_msg
                    else:
                        msg_passed = msg == []
                    PanelState_passed = PanelState == PanelState_val if k[1] is True else PanelState != PanelState_val

                    # Получаем значение Out и значение уставки для формирования сообщения по проверке.
                    Out = read_float(address=OUT_REGISTER)
                    setpoint_value = read_float(address=LEGS[set_name]['register'])

                    if mode == 'Oos':
                        if (st1 and PanelState and leg) is False and msg == []:
                            print_text_grey(f'  Уставка {set_name} отработала верно при значении уставки '
                                            f'{set_name}={setpoint_value}, Hyst={hyst} и значении в '
                                            F'Out={round(Out, 1)}    {k[0]}')
                        else:
                            not_error = False
                            print_error(f'{k[0]}  Проверка уставки {set_name} провалилась при значении уставки '
                                        f'{set_name}={setpoint_value}, Hyst={hyst} и значении в Out={round(Out, 1)}:')
                            if st1 is True:
                                print_error(f'    - Status1 сформирован не верно. Значение {number_bit_st1} бита '
                                            f'- {st1}, а ожидалось False')
                            if PanelState is True:
                                print_error(f'    - PanelState сформирован не верно. Значение {PanelState}, '
                                            f'а ожидалось False')
                            if leg is True:
                                print_error(f'    - Значение на ножку с адресом {leg_register} пришло не верное. '
                                            f'Пришло {leg},а ожидалось False')
                            if msg_passed != []:
                                print_error(f'    - Сообщения сформированы не верно. '
                                            f'Пришло {msg},а ожидалось []')
                    else:
                        if st1 is k[1] and PanelState_passed is True and leg is leg_k1 and msg_passed is True:
                            print_text_grey(f'  Уставка {set_name} отработала верно при значении уставки '
                                            f'{set_name}={setpoint_value}, Hyst={hyst} и значении в '
                                            F'Out={round(Out, 1)}    {k[0]}')
                        else:
                            not_error = False
                            print_error(f'{k[0]}  Проверка уставки {set_name} провалилась при значении уставки '
                                        f'{set_name}={setpoint_value}, Hyst={hyst} и значении в Out={round(Out, 1)}:')
                            if st1 is not k[1]:
                                print_error(f'    - Status1 сформирован не верно. Значение {number_bit_st1} бита '
                                            f'- {st1}, а ожидалось {k[1]}')
                            if PanelState_passed is False:
                                print_error(f'    - PanelState сформирован не верно. Значение {PanelState}, '
                                            f'а ожидалось {PanelState_val}')
                            if leg is not leg_k1:
                                print_error(f'    - Значение на ножку с адресом {leg_register} пришло не верное. '
                                            f'Пришло {leg},а ожидалось {leg_k1}')
                            if msg_passed is False:
                                print_error(f'    - Сообщения сформированы не верно. '
                                            f'Пришло {msg},а ожидалось {expected_msg if len(k) == 3 else []}')
                print() if not_error is False or DETAIL_REPORT_ON is True else None
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_working_setpoint_with_large_jump(not_error):
    print_title('Проверка сработки уставок при изменении значения на величину, '
                'которая затрагивает сразу несколько уставок в режимах Fld, Imit и Tst.')

    # Создаем словарь для проверки.
    data = {
        'AHLim': {'st1': [True,  False, False, False, False, False], 'bit': 14, 'message': [114], 'msg_Imit': [164]},
        'WHLim': {'st1': [False, True,  False, False, False, False], 'bit': 13, 'message': [113], 'msg_Imit': [163]},
        'THLim': {'st1': [False, False, True,  False, False, False], 'bit': 12, 'message': [112], 'msg_Imit': [162]},
        'TLLim': {'st1': [False, False, False, True,  False, False], 'bit': 10, 'message': [110], 'msg_Imit': [160]},
        'WLLim': {'st1': [False, False, False, False, True,  False], 'bit':  9, 'message': [109], 'msg_Imit': [159]},
        'ALLim': {'st1': [False, False, False, False, False,  True], 'bit':  8, 'message': [108], 'msg_Imit': [158]}
    }

    # Включаем все уставки. Проходим по всем режимам циклом.
    on_or_off_all_setpoint(required_bool_value=True)
    for mode in ('Imit', 'Fld', 'Tst'):
        print_text_white(f'Проверка уставок в режиме {mode}.')
        turn_on_mode(mode=mode)

        # Создаем переменную со знаком для функции set_value_AP. Cоздаем список битов для чтения status1.
        sign = '>'
        numbers_bit = [data_value['bit'] for data_value in data.values()]

        # Проходим циклом по словарю data и проверяем сработку уставок.
        for setpoint, data_param in data.items():

            # Устанавливаем значения в Input больше или меньше, чем значение уставки в зависимости от стадии проверки.
            sign = '<' if setpoint == 'TLLim' else sign
            Input = set_value_AP(sign=sign, setpoint=setpoint, mode=mode)
            midle_Out = (START_VALUE['MaxEV']['start_value'] - START_VALUE['MinEV']['start_value']) / 2
            midle_Range_input = START_VALUE['RangeMax']['start_value'] / 2 + START_VALUE['RangeMin']['start_value'] / 2
            start_input = midle_Range_input if mode != 'Imit' else midle_Out
            input_leg = LEGS['Input']['register'] if mode != 'Imit' else LEGS['ImitInput']['register']

            # Устанавливаем занчение АП в стартовое. Читаем сообщения, а затем устанавливаем значение в Input.
            write_holding_registers(address=input_leg, values=start_input)
            old_messages = read_all_messages()
            write_holding_registers(address=input_leg, values=Input)

            # Проверяем что в status1 в соответствующих битах, читаем сообщения и сравниваем с эталоном из data.
            new_messages = read_new_messages(old_messages)
            st1 = [read_status1_one_bit(number_bit=number_bit) for number_bit in numbers_bit]
            data_st1 = data_param['st1']
            data_message = data_param['message'] if mode != 'Imit' else data_param['msg_Imit']
            if st1 == data_st1 and new_messages == data_message:
                print_text_grey(f'Проверка уставки {setpoint} пройдена. Сообщения и status1 сформированы верно.')
            else:
                not_error = False
                if st1 != data_st1:
                    print_error(f'Ошибка! При проверке уставки {setpoint} сформирован неверный status1. '
                                f'Получен {st1}, а ожидалось {data_st1}.')
                if new_messages != data_message:
                    print_error(f'Ошибка! При проверке уставки {setpoint} обнаружена ошибка в формировании сообщений. '
                                f'Сформировано {new_messages} а ожидалось {data_message}.')

            # Возвращаем значение Input в исходное положение.
            write_holding_registers(address=input_leg, values=start_input)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_work_at_out_in_range_min_ev_and_max_ev_tst_and_fld(not_error):  # НУЖНО БУДЕТ ПРОВЕРИТЬ, КАК ИСПРАВЯТ ПО. Проверка сработки/несработки выхода за пределы инженерных значений (MinEV и MaxEV).
    print_title('Проверка сработки/несработки выхода за пределы инженерных значений (MinEV и MaxEV) \n'
                'в режимах Fld и Tst.')

    # Создаем словарь для проверки.
    data = {
        'MinEV > 0, MaxEV > 0': {'№': 1, 'MinEV': 11.1,   'MaxEV': 99.9},
        'MinEV = 0, MaxEV > 0': {'№': 2, 'MinEV': 0,      'MaxEV': 888.8},
        'MinEV < 0, MaxEV > 0': {'№': 3, 'MinEV': -100,   'MaxEV': 100},
        'MinEV < 0, MaxEV = 0': {'№': 4, 'MinEV': -999.3, 'MaxEV': 0},
        'MinEV < 0, MaxEV < 0': {'№': 5, 'MinEV': -123.4, 'MaxEV': -32.01}
    }

    # Включаем режим. Находим 1% от рабочего диапазона Input.
    for mode in ('Tst', 'Fld'):
        turn_on_mode(mode=mode)
        RangeMax_value = START_VALUE['RangeMax']['start_value']
        RangeMin_value = START_VALUE['RangeMin']['start_value']
        one_percent_of_input = (RangeMax_value - RangeMin_value) * 0.01
        print_text_white(f'\nПроверка режима {mode}.')

        # Формируем кортеж со значениями для проверки.
        # (Эталонные сообщения, номер бита для st2 и PanelAlm, значение бита, значение в Input.)
        print_error('НА ДАННЫЙ МОМЕНТ ЕСТЬ ВОПРОС ПО СООБЩЕНИЮ 200, 202, 250 И 252. ОНИ ОТНОСЯТСЯ К ОБРЫВУ И КЗ.\n'
                    'НУЖНО ЛИБО СДЕЛАТЬ ПЕРЕИМЕНОВАТЬ ЭТИ СООБЩЕНИЯ, '
                    'ЛИБО СДЕЛАТЬНОВЫЕ ИМЕННО НА ВЫХОД ЗА ГРАНИЦЫ Max/MinEV\n\n'
                    '!!!!!!!!!!!! ТЕСТЫ НЕ ПРОХОДЯТ ИЗ-ЗА НЕДОЧЕТА С ">=" В ПО !!!!!!!!!!!!!!!!!!!!\n')
        status_values_and_values_input_for_check = (
            ([],              STATUS2['HightErr'], False, RangeMax_value),
            ([],              STATUS2['HightErr'], False, RangeMax_value + one_percent_of_input - 0.01),
            ([200, 212],      STATUS2['HightErr'], True,  RangeMax_value + one_percent_of_input),
            ([],              STATUS2['HightErr'], True,  RangeMax_value + one_percent_of_input + 0.01),
            ([],              STATUS2['HightErr'], True,  RangeMax_value + one_percent_of_input),
            ([],              STATUS2['HightErr'], True,  RangeMax_value + one_percent_of_input - 0.01),
            ([111, 250, 262], STATUS2['HightErr'], False, RangeMax_value),
            ([],              STATUS2['HightErr'], False, RangeMax_value - 0.01),
            ([],              STATUS2['LowErr'],   False, RangeMin_value),
            ([],              STATUS2['LowErr'],   False, RangeMin_value - one_percent_of_input + 0.01),
            ([202, 212],      STATUS2['LowErr'],   True,  RangeMin_value - one_percent_of_input),
            ([],              STATUS2['LowErr'],   True,  RangeMin_value - one_percent_of_input - 0.01),
            ([],              STATUS2['LowErr'],   True,  RangeMin_value - one_percent_of_input),
            ([],              STATUS2['LowErr'],   True,  RangeMin_value - one_percent_of_input + 0.01),
            ([111, 252, 262], STATUS2['LowErr'],   False, RangeMin_value),
            ([],              STATUS2['LowErr'],   False, RangeMin_value + 0.01),
        )

        # Проходимся в цикле по словарю data. Выставляем значения MinEV и MaxEV.
        for name_cheking, data_value in data.items():
            number_check = data_value['№']
            MinEV_val = data_value['MinEV']
            MaxEV_val = data_value['MaxEV']
            write_min_max_EV(MinEV=MinEV_val, MaxEV=MaxEV_val)
            print_text_white(f'\n{number_check}) Проверка случая {name_cheking} со значениями '
                             f'MinEV={MinEV_val}, MaxEV={MaxEV_val}')

            # Читаем сообщения и подcтавляем значения из кортежа values_input_for_check в Input.
            for msg, number_bit_st2_and_PanelAlm, result, value_in_input in status_values_and_values_input_for_check:
                old_messages = read_all_messages()
                write_holding_registers(address=INPUT_REGISTER, values=value_in_input)
                Out = round(read_float(address=OUT_REGISTER), 2)

                # Читаем значение 7 бита status1, 4 или 5 бит status2 и PanelAlm, PanelState, ножку Bad и сообщения.
                st1 = read_status1_one_bit(number_bit=STATUS1['Bad'])
                st2 = read_status2_one_bit(number_bit=number_bit_st2_and_PanelAlm)
                PanelAlm = read_PanelAlm_one_bit(number_bit=number_bit_st2_and_PanelAlm)
                PanelState = read_PanelState()
                PanelState_bad = PANELSTATE['Bad']
                PanelState_res = read_PanelState() == PanelState_bad
                new_msg = read_new_messages(old_messages)
                Bad = read_discrete_inputs(address=BAD_REGISTER, bit=0)
                Bad_result = False if mode == 'Tst' else result

                # Проверяем сработку превышения инженерного значения.
                if (st1 and st2 and PanelAlm and PanelState_res) is result and new_msg == msg and Bad is Bad_result:
                    print_text_grey(f'   Проверка пройдена при Out={Out} пройдена. Status1, Status2, PanelAlm, '
                                    'PanelState и сообщения сформированы верно.')
                else:
                    print_error(f'   Проверка провалена при Out={Out}:')
                    not_error = False
                    if Bad is not Bad_result:
                        print_error(f'    - Ошибка сигнала на ножке Bad. Пришло {Bad}, а ожидалось {Bad_result}.')
                    if st1 is not result:
                        print_error(f'    - Ошибка в формировании Status1. В 7 бите {st1}, а ожидалось {result}.')
                    if st2 is not result:
                        print_error(f'    - Ошибка в формировании Status2. В {number_bit_st2_and_PanelAlm} '
                                    f'бите пришло {st2}, а ожидалось {result}.')
                    if PanelAlm is not result:
                        print_error(f'    - Ошибка в формировании PanelAlm. В {number_bit_st2_and_PanelAlm} '
                                    f'бите пришло {PanelAlm}, а ожидалось {result}.')
                    if PanelState_res is not result:
                        print_error(f'    - Ошибка в формировании PanelState. Пришло {PanelState}, '
                                    f'а ожидалось {PanelState_bad}.')
                    if new_msg != msg:
                        print_error(f'    - Ошибка в формировании сообщений. Пришло {new_msg}, а ожидалось {msg}.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_kvitir(not_error):  # ПРОВЕРКА ТОЛЬКО НА УСТАВКЕ 'THLim' ВОЗМОЖНО ТРЕБУЕТСЯ ПРОВЕРИТЬ НА ВСЕХ УСТАВКАХ.
    print_title('Проверка работоспособности квитирования. Возникновение при переходе через уставку.')
    print_error('ПРОВЕРКА ТОЛЬКО НА УСТАВКЕ "THLim" ВОЗМОЖНО ТРЕБУЕТСЯ ПРОВЕРИТЬ НА ВСЕХ УСТАВКАХ.')

    # Включаем уставку 'THLim'. Квитируем. Проверяем в status1 требуется ли квитирование.
    switch_position(command='THLimEn', required_bool_value=True)
    reset_CmdOp()
    write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP['Kvitir'])
    if read_status1_one_bit(number_bit=STATUS1['Kvitir']) is True:
        print_error('Ошибка! Невозможно квитировать. Дальнейший тест нецелесообразен.')
        not_error = False
        return not_error

    # Читаем сообщения. Передаем значение в Input больше уставки 'THLim'.
    old_messages = read_all_messages()
    set_value_AP(sign='>', setpoint='THLim')

    # Проверяем сработала ли уставка.
    st1_THAct = read_status1_one_bit(number_bit=STATUS1['THAct'])
    if st1_THAct is False:
        print_error('Ошибка! Уставка не сработала. Дальнейший тест нецелесообразен.')
        not_error = False
        return not_error

    # Проверяем включения сигнала "Требуется квитирование".
    not_error = check_work_kvitir_on(not_error=not_error, old_messages=old_messages, msg=[112])

    # Читаем сообщения. Квитируем. Проверяем сработку квитирования.
    old_messages = read_all_messages()
    reset_CmdOp()
    write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP['Kvitir'])

    # Проверяем отключения сигнала "Требуется квитирование".
    not_error = check_work_kvitir_off(not_error=not_error, old_messages=old_messages)

    # Читаем сообщения. Передаем значение в Input меньше уставки 'THLim'.
    old_messages = read_all_messages()
    set_value_AP(sign='<', setpoint='THLim')

    # Проверяем снята ли уставка.
    st1_THAct = read_status1_one_bit(number_bit=STATUS1['THAct'])
    if st1_THAct is True:
        print_error('Ошибка! Уставка не снимается. Дальнейший тест нецелесообразен.')
        not_error = False
        return not_error

    # # Проверяем что сигнал "Требуется квитирование" по прежнему снят.
    # not_error = check_work_kvitir_off(not_error=not_error, old_messages=old_messages)
    # Проверяем что сигнал "Требуется квитирование" по появился.
    not_error = check_work_kvitir_on(not_error=not_error, old_messages=old_messages, msg=[111])
    print_error('ТУТ ПОКА ВОПРОС. НЕ ПОНЯТНО КАК ДОЛЖНО РАБОТАТЬ КВИТИРОВАНИЕ. СЕЙЧАС ПРИ ПЕРЕСКОКЕ ЧЕРЕЗ УСТАВКУ  в любом направление через уставку, возникает требование квитировать')
    return not_error


# ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"
@reset_initial_values
@writes_func_failed_or_passed
# Проверка возможности включения режима "Имитация".
def checking_simulation_mode_turn_on(not_error):
    print_title('Проверка возможности включения режима "Имитация".')

    # Проверяем, что включен режим, отличный от "Имитация" через PanelMode и Status1.
    Imit_PanelMode = PANELMODE['Imit']
    if read_PanelMode() == Imit_PanelMode and read_status1_one_bit(number_bit=STATUS1['Imit']) is True:
        print_error('Был включен режим "Имитация". Проверь работоспособность декоратора reset_initial_values')

    # Читаем сообщения. Устанавливаем через CmdOp режим "Имитация".
    old_messages = read_all_messages()
    write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP['Imit'])

    # Читаем сообщения. Проверяем PanelMode и Status1.
    st1 = read_status1_one_bit(number_bit=STATUS1['Imit'])
    PanelMode = read_PanelMode()
    new_msg = read_new_messages(old_messages)
    if st1 is True and PanelMode == Imit_PanelMode and new_msg == [2, 54, 20200]:
        print_text_grey('Проверка возможности включения режима "Имитация" пройдена.')
    else:
        not_error = False
        print_error('Ошибка! Проверка возможности включения режима "Имитация" провалена:')
        if st1 is False:
            print_error(f'  - В Status1 пришло {st1}, а ожидалось True.')
        if PanelMode != Imit_PanelMode:
            print_error(f'  - В PanelMode пришло {PanelMode}, а ожидалось {Imit_PanelMode}.')
        if new_msg != []:
            print_error(f'  - Сформированы сообщения {new_msg}, а ожидалось {[2, 54, 20200]}.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка неизменности значений DeltaV, Period, ImitInput, MaxEV, MinEV, T01, SpeedLim,
# AHLim, WHLim, THLim, TLLim, WLLim, ALLim, Hyst, Kf, а также сохранения положения переключателей
# (SpeedOff, MsgOff, FiltOff, ALLimEn, WLLimEn, TLLimEn, THLimEn, WHLimEn, AHLimEn) при переключениях между режимами.
def checking_values_when_switching_modes(not_error):
    print_title('Проверка неизменности значений DeltaV, Period, ImitInput, MaxEV, MinEV, T01, SpeedLim,\n'
                'AHLim, WHLim, THLim, TLLim, WLLim, ALLim, Hyst, Kf, а также сохранения положения переключателей.\n'
                '(SpeedOff, MsgOff, FiltOff, ALLimEn, WLLimEn, TLLimEn, THLimEn, WHLimEn, AHLimEn)'
                'при переключениях между режимами.')

    # Создаем переменную с кортежем из всех параметров для проверки. 
    params_for_check = ('DeltaV', 'Period', 'ImitInput', 'MaxEV', 'MinEV', 'T01', 'SpeedLim',
                        'AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim', 'Hyst', 'Kf')

    # Создаем вспомогательную функцию для формирования словаря значений параметров и переключателей.
    def get_checklist():
        checklist = [(param, read_float(address=START_VALUE[param]['register'])) for param in params_for_check]
        checklist.extend(
            [(name, read_status1_one_bit(number_bit=number_bit['st1'])) for name, number_bit in SWITCH.items()]
        )
        return checklist

    # Создаем вспомогательную функцию для проверки.
    def base_check(not_error):

        # Проходим двойным циклом по кортежу с командами для переключения в разные режимы.
        for mode1 in ('Fld', 'Tst', 'Oos', 'Imit'):
            for mode2 in ('Fld', 'Tst', 'Oos', 'Imit'):

                # Если они совпадают, то не проводим проверку.
                if mode1 == mode2:
                    break

                # Включаем режим переданный в параметре "mode1".
                not_error = turn_on_mode(mode=mode1)

                # Создаем список для записи всех значений параметров и переключателей в режиме mode1.
                checklist_before = get_checklist()

                # Включаем режим "mode2". Сравниваем checklist_before со списком, полученным после переключения режима.
                not_error = turn_on_mode(mode=mode2)
                checklist_after = get_checklist()
                if checklist_before == checklist_after:
                    print_text_grey(f'Проверка переключения с {mode1} на {mode2} прошла успешно.')
                else:
                    not_error = False

                    # Выводим сообщение об ошибке со списком изменившихся параметров и переключателей.
                    print_error('Ошибка! Следующие параметры отличаются:')
                    for i in range(len(checklist_after)):
                        if checklist_before[i] != checklist_after[i]:
                            print_error(f'  - {checklist_before[i][0]}: до - '
                                        f'{checklist_before[i][1]}, после - {checklist_after[i][1]}')
        return not_error

    # Проводим проверку с выключателями в положении False.
    print_text_white('Старт проверки с пеерключателями в положении False.')
    not_error = base_check(not_error=not_error)

    # Выставляем все переключатели в положение True. Проводим проверку повторно.
    for command in SWITCH.keys():
        switch_position(command=command, required_bool_value=True)
    print_text_white('Старт проверки с пеерключателями в положении True.')
    not_error = base_check(not_error=not_error)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка переключения значения АП с Input на ImitInput при переключении с режимов
# "Полевая обработка", "Тестирование", "Маскирование" на режим "Имитация" и обратно.
def checking_input_in_simulation_mode(not_error):
    print_title('Проверка переключения значения АП с Input на ImitInput при переключении с режимов\n'
                '"Полевая обработка", "Тестирование", "Маскирование" на режим "Имитация" и обратно.')

    # Проходим циклом по списку с командами для переключения в разные режимы из режима "Имитация".
    for mode in ('Fld', 'Tst', 'Oos'):

        # Вызывем функцию, которая проводит проверку и присваиваем результат ее работы в переменную not_error.
        not_error = values_out_when_turn_on_simulation_mode(mode=mode, not_error=not_error)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка корректности изменения значения АП в режиме «Имитация».
def checking_simulation_mode_when_change_input_and_imitinput(not_error):
    print_title('Проверка корректности изменения значения в режиме «Имитация» при записи в Input и ImitInput.')

    # Включаем режим "Имитация".
    if turn_on_mode(mode='Imit') is False:
        not_error = False
        print_error('Ошибка! Не удалось включить режим "Имитация". Дальнейшее тестирование нецелесообразно.')

    # Читаем значение в Out и OutmA.
    Out_before = read_float(address=OUT_REGISTER)
    OutmA_before = read_float(address=OUTMA_REGISTER)

    # Меняем значение в Input на +1.1 и проверяем, чтобы OutmA изменился, а Out нет.
    write_holding_registers(address=LEGS['Input']['register'], values=(START_VALUE['Input']['start_value'] + 1.1))
    Out_after = read_float(address=OUT_REGISTER)
    OutmA_after = read_float(address=OUTMA_REGISTER)
    if Out_before == Out_after and OutmA_before != OutmA_after:
        print_text_grey('Проверка изменения значения Input в режиме "Имитация" пройдена.')
    else:
        not_error = False
        print_error('Ошибка! изменения значения Input в режиме "Имитация" провалена:')
        if Out_before != Out_after:
            print_error(f' - Значение в Out изменилось, а не должно было. Out={Out_after}, а был {Out_before}')
        if OutmA_before == OutmA_after:
            print_error(' - Значение OutmA не изменилось, а должно было.')

    # Меняем значение в ImitInput на +1.1 и проверяем, чтобы Out изменился, а OutmA нет.
    write_holding_registers(
        address=LEGS['ImitInput']['register'], values=(START_VALUE['ImitInput']['start_value'] + 1.1)
    )
    Out_before = Out_after
    OutmA_before = OutmA_after
    Out_after = read_float(address=OUT_REGISTER)
    OutmA_after = read_float(address=OUTMA_REGISTER)
    if Out_before != Out_after and OutmA_before == OutmA_after:
        print_text_grey('Проверка изменения значения ImitInput в режиме "Имитация" пройдена.')
    else:
        not_error = False
        print_error('Ошибка! изменения значения ImitInput в режиме "Имитация" провалена:')
        if Out_before == Out_after:
            print_error(f' - Значение в Out не изменилось, а должно было. Out={Out_after}, а был {Out_before}')
        if OutmA_before != OutmA_after:
            print_error(' - Значение OutmA изменилось, а не должно было.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка на непрохождении сигнала недостоверности значения АП при выходе Input за пределы MinEV и MaxEV.
def checking_absence_unreliability_value_min_ev_and_max_ev_in_imit_and_oos(not_error):
    print_title('Проверка на непрохождении сигнала недостоверности значения АП \n'
                'при выходе Input за пределы MinEV и MaxEV.')

    # Создаем словарь для проверки.
    data = {
        'MinEV > 0, MaxEV > 0': {'№': 1, 'MinEV': 11.1,   'MaxEV': 99.9},
        'MinEV = 0, MaxEV > 0': {'№': 2, 'MinEV': 0,      'MaxEV': 888.8},
        'MinEV < 0, MaxEV > 0': {'№': 3, 'MinEV': -100,   'MaxEV': 100},
        'MinEV < 0, MaxEV = 0': {'№': 4, 'MinEV': -999.3, 'MaxEV': 0},
        'MinEV < 0, MaxEV < 0': {'№': 5, 'MinEV': -123.4, 'MaxEV': -32.01}
    }

    # Переключаем режим в цикле и проводим проверку. Задаем значения MinEV и MaxEV.
    for mode in ('Imit', 'Oos'):
        not_error = turn_on_mode(mode=mode)
        RangeMax_value = START_VALUE['RangeMax']['start_value']
        RangeMin_value = START_VALUE['RangeMin']['start_value']
        print_text_white(f'\nПроверка режима {mode}.')

        # Формируем кортеж со значениями для проверки.
        status_values_and_values_input_for_check = (
            ([], STATUS2['HightErr'], False, RangeMax_value + RangeMax_value),
            ([], STATUS2['LowErr'],   False, RangeMin_value - RangeMin_value),
        )

        # Проходимся в цикле по data. Выставляем значения MinEV, MaxEV и ImitInput так, чтобы он был внутри диапазона.
        for name_cheking, data_value in data.items():
            number_check = data_value['№']
            MinEV_val = data_value['MinEV']
            MaxEV_val = data_value['MaxEV']
            ImitInput = (MinEV_val + MaxEV_val) / 2
            write_min_max_EV(MinEV=MinEV_val, MaxEV=MaxEV_val)
            write_holding_registers(address=LEGS['ImitInput']['register'], values=ImitInput)
            print_text_white(f'\n{number_check}) Проверка случая {name_cheking} со значениями '
                             f'MinEV={MinEV_val}, MaxEV={MaxEV_val}')

            # Читаем сообщения и подcтавляем значения из кортежа values_input_for_check в Input.
            for msg, number_bit_st2_and_PanelAlm, result, value_in_input in status_values_and_values_input_for_check:
                old_messages = read_all_messages()
                write_holding_registers(address=INPUT_REGISTER, values=value_in_input)
                Out = round(read_float(address=OUT_REGISTER), 2)

                # Читаем значение 7 бита status1, 4 или 5 бит status2, 4 или 5 бит PanelAlm, PanelState и сообщения.
                st1 = read_status1_one_bit(number_bit=STATUS1['Bad'])
                st2 = read_status2_one_bit(number_bit=number_bit_st2_and_PanelAlm)
                PanelAlm = read_PanelAlm_one_bit(number_bit=number_bit_st2_and_PanelAlm)
                PanelState = read_PanelState()
                PanelState_bad = PANELSTATE['Bad']
                PanelState_res = read_PanelState() == PanelState_bad
                new_msg = read_new_messages(old_messages)

                # Проверяем сработку превышения инженерного значения.
                if (st1 and st2 and PanelAlm and PanelState_res) is result and new_msg == msg:
                    print_text_grey(f'   Проверка пройдена при Out={Out} пройдена. Status1, Status2, PanelAlm, '
                                    'PanelState и сообщения сформированы верно.')
                else:
                    print_error(f'   Проверка провалена при Out={Out}:')
                    not_error = False
                    if st1 is not result:
                        print_error(f'    - Ошибка в формировании Status1. В 7 бите пришло {st1},'
                                    f' а ожидалось {result}.')
                    if st2 is not result:
                        print_error(f'    - Ошибка в формировании Status2. В {number_bit_st2_and_PanelAlm} '
                                    f'бите пришло {st2}, а ожидалось {result}.')
                    if PanelAlm is not result:
                        print_error(f'    - Ошибка в формировании PanelAlm. В {number_bit_st2_and_PanelAlm} '
                                    f'бите пришло {PanelAlm}, а ожидалось {result}.')
                    if PanelState_res is not result:
                        print_error(f'    - Ошибка в формировании PanelState. Пришло {PanelState}, '
                                    f'а ожидалось {PanelState_bad}.')
                    if new_msg != msg:
                        print_error(f'    - Ошибка в формировании сообщений. Пришло {new_msg}, а ожидалось {msg}.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка на непрохождении сигнала недостоверности значения АП при неисправности
# модуля, канала, датчика и внешней ошибке в режимах "Имитация", "Маскирование".
def checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking(not_error):
    print_title('Проверка на непрохождении сигнала недостоверности значения АП при '
                'неисправности модуля, канала, датчика и внешней ошибке. '
                'в режимах "Имитация", "Маскирование".')

    # Проходим циклом по всем режимам работы (кроме режима "Fld"), включаем поочередно и тестируем.
    for mode in ('Oos', 'Imit'):
        turn_on_mode(mode=mode)

        # В цикле проходим по всем ошибкам.
        for error in ['ChFlt', 'ModFlt', 'SensFlt', 'ExtFlt']:

            # Читаем сообщения. Устанавливаем сигнал недостоверности.
            old_messages = read_all_messages()
            switch_position_for_legs(command=error, required_bool_value=True)

            # Читаем новые сообщения, Status1, Status2, PanelAlm, PanelState и выполняем проверку.
            number_bit_st2 = STATUS2[error]
            PanelState_Bad = PANELSTATE['Bad']
            new_messages = read_new_messages(old_messages)
            st1 = read_status1_one_bit(number_bit=STATUS1['Bad'])
            st2 = read_status2_one_bit(number_bit=number_bit_st2)
            PanelAlm = read_PanelAlm_one_bit(number_bit=number_bit_st2)
            PanelState = read_PanelState()

            if new_messages == [] and (st1 and st2 and PanelAlm) is False and PanelState != PanelState_Bad:
                print_text_grey(f'В режиме {mode} проверка непрохождения сигнала '
                                f'{error}({VALUE_UNRELIABILITY[error]}) прошла успешно.')
            else:
                not_error = False
                print_error(f'В режиме {mode} произошла ошибка при проверке непрохождения сигнала '
                            f'{error}({VALUE_UNRELIABILITY[error]}).')
                if new_messages != []:
                    print_error(f' - Пришли сообщения {new_messages}, хотя не должны были.')
                if st1 is True:
                    print_error(' - В Status1 7 бит равен True, а должен быть False.')
                if st2 is True:
                    print_error(f' - В Status2 {number_bit_st2} бит равен True, а должен быть False.')
                if PanelAlm is True:
                    print_error(f' - В PanelAlm {number_bit_st2} бит равен True, а должен быть False.')
                if PanelState == PanelState_Bad:
                    print_error(f' - В PanelState пришло {PanelState} , а ожидалось {PanelState_Bad}.')

            # Снимаем сигнал недостоверности.
            switch_position_for_legs(command=error, required_bool_value=False)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_off_messages_and_statuses_and_kvitir_in_masking_mode(not_error):  # Делаю.
    print_title('Проверка отсутствия генерации сообщений и статусов, при режиме "Маскирование".')

    # Включаем режим "Маскирование". Читаем сообщения. Устанавливаем сигнал недостоверности.
    turn_on_mode(mode='Oos')
    old_messages = read_all_messages()
    write_holding_registers(address=LEGS['Input']['register'], values=25)

    # Читаем сообщения, статусы и ножку Bad, бит квитирования. Выполняем проверку.
    new_messages = read_new_messages(old_messages)
    st1 = read_status1_one_bit(number_bit=STATUS1['Bad'])
    st1_kvit = read_status1_one_bit(number_bit=STATUS1['Kvitir'])
    st2 = read_status2_one_bit(number_bit=STATUS2['HightErr'])
    PanelAlm = read_PanelAlm_one_bit(number_bit=STATUS2['HightErr'])
    PanelState = read_PanelState() == PANELSTATE['Oos']
    Bad = read_discrete_inputs(address=BAD_REGISTER, bit=0)
    if new_messages == [] and PanelState and (st1 and st2 and PanelAlm and Bad and st1_kvit) is False:
        print_text_grey('Проверка отсутствия генерации сообщений и статусов, при режиме "Маскирование" прошла успешно.')
    else:
        not_error = False
        print_error('При проверке отсутствия генерации сообщений и статусов, при режиме "Маскирование" '
                    'произошла ошибка.')
        if new_messages != []:
            print_error(f' - Пришли сообщения {new_messages}, хотя не должны были.')
        if st1 is True:
            print_error(' - В Status1 7 бит равен True, а должен быть False.')
        if st2 is True:
            print_error(f' - В Status2 {STATUS2["HightErr"]} бит равен True, а должен быть False.')
        if PanelAlm is True:
            print_error(f' - В PanelAlm {STATUS2["HightErr"]} бит равен True, а должен быть False.')
        if PanelState != PANELSTATE['Oos']:
            print_error(f' - В PanelState пришло {PanelState} , а ожидалось {PANELSTATE["Oos"]}.')
        if Bad is True:
            print_error(f' - В Bad пришло {Bad} , а ожидалось False.')
        if st1_kvit is True:
            print_error(' - Квитирование не работает. В Status1 31 бит равен True , а ожидалось False.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка несработки уставок при изменении значения в Input в режиме "Имитация".
def checking_work_setpoint_in_imit_mode_when_write_input(not_error):
    print_title('Проверка несработки уставок при изменении значения в Input в режиме "Имитация".')

    # Включаем режим "Имитация". Задаем значение ImitInput.
    turn_on_mode(mode='Imit')
    Imit_value = (START_VALUE['MaxEV']['start_value'] - START_VALUE['MinEV']['start_value']) / 2
    write_holding_registers(address=LEGS['ImitInput']['register'], values=Imit_value)

    # Включаем все уставки. Задаем стартовое значение переменной для Input.
    on_or_off_all_setpoint(required_bool_value=True)
    Input_start = START_VALUE['RangeMax']['start_value'] - 1

    # Изменяем значение в Input для вызова сработки разных уставок в цикле.
    for setpoint in ('AHLim', 'WHLim', 'THLim', 'TLLim', 'WLLim', 'ALLim'):

        # Меняем Input, если отработали все верхние уставки. Читаем сообщения. Меняем значений в Input.
        Input = START_VALUE['RangeMin']['start_value'] + 1 if setpoint == 'TLLim' else Input_start
        old_messages = read_all_messages()
        write_holding_registers(address=LEGS['Input']['register'], values=Input)

        # Читаем сообщения, статусы и ножки. Выполняем проверку. # Возмвращаем Input в исходное состояние.
        setpointEn = f'{setpoint}En'
        setpointAct = f'{setpoint[:2]}Act'
        new_messages = read_new_messages(old_messages)
        st1 = read_status1_one_bit(number_bit=STATUS1[setpointAct])
        PanelState = read_PanelState()
        leg = read_discrete_inputs(address=START_VALUE[setpointEn]['register'])
        if new_messages == [] and (PanelState and st1 and leg) is False:
            print_text_grey(f'Проверка несработки уставок при изменении значения в Input, при режиме "Имитация" '
                            f'прошла успешно для уставки {setpoint}.')
        else:
            not_error = False
            print_error(f'При проверке несработки уставок при изменении значения в Input, при режиме "Имитация" '
                        f'произошла ошибка для уставки {setpoint}.')
            if new_messages != []:
                print_error(f' - Пришли сообщения {new_messages}, хотя не должны были.')
            if st1 is True:
                print_error(f' - В Status1 {STATUS1[setpointAct]} бит равен True, а должен быть False.')
            if PanelState is True:
                print_error(f' - В PanelState пришло {PanelState} , а ожидалось False.')
            if leg is True:
                print_error(f' - Ножка {START_VALUE[setpointEn]["register"]} пришла True, а ожидалось False.')
        write_holding_registers(address=LEGS['Input']['register'], values=START_VALUE['Input']['start_value'])
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_switching_between_modes_in_case_of_errors(not_error):
    print_title('Проверка возможности перехода из режима "Маскирование" в другие режимы при неисправностях \n'
                'канала, модуля, сенсора,внешней ошибки и выхода за пределы границ измерений.')
    print_error('НЕПРОХОДИТ ПОТОМУ ЧТО НУЖНЫ ОШИБКИ 201 И 203 (СМОТРИ В ДЕБАГЕ)')

    # Подготавливаем список возможных ошибок.
    switches = [('ChFlt', [204]), ('ModFlt', [206]), ('SensFlt', [208]),
                ('ExtFlt', [210]), ('HightErr', [201]), ('LowErr', [203])]
    work_modes_and_message = (('Imit', [2, 51, 20200]), ('Fld', [4, 51, 20400]), ('Tst', [5, 51, 20500]))

    # Перебираем все возможные комбинации от 1 до 5 одновременных ошибок.
    for r in range(1, 6):
        # В цикле перебираем возможные комбинации ошибок.
        for combo_error in combinations(switches, r):
            # Пропускаем комбинацию, где одновременно срабатывает выход за верх и низ инженерных величин.
            if ('HightErr', [200]) in combo_error and ('LowErr', [202]) in combo_error:
                continue

            # Переходим в режим Oos на старте, выключаем ошибки и приводим Input в рабочий диапазон.
            not_error = turn_on_mode(mode='Oos')
            write_holding_registers(address=LEGS['Input']['register'], values=START_VALUE['Input']['start_value'])
            write_holding_registers(address=LEGS['ImitInput']['register'], values=50)
            for switch, _ in switches[:4]:
                switch_position_for_legs(command=switch, required_bool_value=False)

            #  Активируем эти ошибки, пробуем переключать режимы и проверяем меняются ли по st1 и PanelMode.
            msg_all = []
            errors = []
            for error, msg_error in combo_error:
                errors.append(error)
                msg_all.extend(msg_error)
                if error == 'HightErr':
                    write_holding_registers(address=LEGS['Input']['register'], values=200)
                    write_holding_registers(address=LEGS['ImitInput']['register'], values=1225)
                elif error == 'LowErr':
                    write_holding_registers(address=LEGS['Input']['register'], values=-200)
                    write_holding_registers(address=LEGS['ImitInput']['register'], values=-1225)
                else:
                    switch_position_for_legs(command=error, required_bool_value=True)
            for mode, msg_mode in work_modes_and_message:
                msg = msg_mode.copy()
                if mode == 'Imit' and error == 'LowErr':
                    msg.extend([202, 212])
                    st1_kvit_original = True
                elif mode == 'Imit' and error == 'HightErr':
                    msg.extend([200, 212])
                    st1_kvit_original = True
                elif mode == 'Fld' or mode == 'Tst':
                    msg.extend(msg_all)
                    msg.extend([212])
                    st1_kvit_original = True
                else:
                    st1_kvit_original = False
                msg.sort()
                old_messages = read_all_messages()
                not_error = turn_on_mode(mode=mode)
                new_messages = read_new_messages(old_messages=old_messages)
                st1 = read_status1_one_bit(number_bit=STATUS1[mode])
                PanelMode = read_PanelMode()
                st1_kvit = read_status1_one_bit(number_bit=STATUS1['Kvitir'])
                if PanelMode == PANELMODE[mode] and st1 is True and st1_kvit is st1_kvit_original and new_messages == msg:
                    print_text_grey(f'Проверка включения режима {mode} при активных ошибках {errors} пройдена.')
                else:
                    not_error = False
                    print_error(f'Ошибка при проверке включения {mode} при активных ошибках {errors}.')
                    if st1 is False:
                        print_error(f'  - в Status1 пришло {st1}, а ожидалось True.')
                    if PanelMode != PANELMODE[mode]:
                        print_error(f'  - в PanelMode пришло {PanelMode}, а ожидалось {PANELMODE[mode]}.')
                    if new_messages != msg:
                        print_error(f'  - Пришли следующие сообщения - {new_messages}, а ожидалось {msg}.')
                    if st1_kvit is not st1_kvit_original:
                        print_error(f'  - в Status1(Квитир.) пришло {st1_kvit}, а ожидалось True.')
                not_error = turn_on_mode(mode='Oos')
            print() if DETAIL_REPORT_ON is True else None
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_the_installation_of_commands_from_different_control_panels(not_error):  # Делаю.
    print_title('Проверка установки команд с разных панелей управления.')

    msg_original = []

    # Проходим циклом по всем командам на СmdOp.
    for command_original, command_int_original in CMDOP.items():
        print_text_white(f'Проверка команды {command_original}.') if DETAIL_REPORT_ON is False else None

        # В цикле выполняем проверку для каждого ПУ.
        for i in range(8):
            old_messages = read_all_messages()

            # Формируем команду по формуле. Читаем сообщения. команда с i=0 считается эталонной.
            command_int_control_panel = command_int_original + (i * 256)
            write_CmdOp(command=command_int_control_panel)
            msg = read_new_messages(old_messages)
            msg_original = msg[-1] if i == 0 else msg_original

            # Смотрим только последнее сообщение.
            if msg_original + i == msg[-1]:
                print_text_grey(f'Проверка команды {command_original} на ПУ №{i} прошла успешно.')
            else:
                not_error = False
                print_error(f'Ошибка проверки команды {command_original} на ПУ №{i}. '
                            f'Пришла команда {msg[-1]}, а ожидалась {msg_original + i}.')
    return not_error


@running_time
@start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ АП.
    '''

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')
    cheking_on_off_AlarmOff()
    checking_messages_on_off_setpoints()
    checking_setpoint_values()
    checking_setpoint_not_impossible_min_more_max()
    checking_work_at_out_in_range_min_ev_and_max_ev_tst_and_fld()
    checking_kvitir()
    checking_the_installation_of_commands_from_different_control_panels()

    print('ОБЩИЕ ПРОВЕРКИ\n')
    checking_errors_writing_registers()
    cheking_on_off_for_cmdop()
    checking_generation_messages_and_msg_off()
    cheking_incorrect_command_cmdop()
    checking_operating_modes()
    checking_signal_transfer_low_level_on_middle_level()
    checking_write_maxEV_and_minEV()
    checking_not_impossible_min_ev_more_max_ev()
    checking_work_setpoint()
    checking_working_setpoint_with_large_jump()
    checking_switching_between_modes_in_case_of_errors()
    checking_DeltaV()
    checking_errors_channel_module_sensor_and_external_error_fld_and_tst()
    checking_SpeedLim()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')
    checking_simulation_mode_turn_on()
    checking_values_when_switching_modes()
    checking_input_in_simulation_mode()
    checking_simulation_mode_when_change_input_and_imitinput()
    checking_absence_unreliability_value_min_ev_and_max_ev_in_imit_and_oos()
    checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking()
    checking_work_setpoint_in_imit_mode_when_write_input()

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    checking_off_messages_and_statuses_and_kvitir_in_masking_mode()


if __name__ == "__main__":
    main()
