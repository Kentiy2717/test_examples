from time import sleep
from assist_function import (
    switch_position,
    switch_position_for_legs,
    compare_out_and_setpoint,
    set_value_AP,
    )
from probably_not_used.constants import DETAIL_REPORT_ON
from constants_FB_AP import (
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
    OUT_REGISTER,
    OUTMA_REGISTER,
    MINEV_REGISTER,
    MAXEV_REGISTER,
    START_VALUE,
    SWITCHES_CMDOP,
    SWITCHES_ST1_PANSIG_MESSAGE as SWITCH,
    STATUS1,
    CMDOP,
    PANELMODE
)
from encode_and_decode import decode_float
from func_print_console_and_write_file import (
    print_title,
    print_error,
    print_passed,
    print_text_grey,
    print_failed_test
)
from read_and_write_functions import (
    reset_CmdOp,
    this_is_write_error,
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
from wrappers import (
    running_time,
    connect_and_close_client,
    start_with_limits_values,
    writes_func_failed_or_passed,
    reset_initial_values
)


@writes_func_failed_or_passed
def checking_errors_writing_registers(not_error):  # Готово.
    print_title('Старт проверки ошибок при записи с отрицательными, положительными и нулевым значениями.')
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


@writes_func_failed_or_passed
def cheking_on_off_for_cmdop(not_error):  # Готово.
    print_title('Старт проверки работы переключателей (командой на CmdOp).')
    for name, description in SWITCHES_CMDOP.items():
        count_error = 0                                                                                                 # Максимально возможное количество ошибок.
        for i in range(0, 4):                                                                                           # Пытаемся переключить каждый выключатель 4 раза (чтобы он остался в первоначальном состоянии).
            Status1_before = read_status1_one_bit(SWITCH[name]['St1'])                                                  # Читаем status1 и запоминаем значение переключателя.
            PanelSig_before = read_PanelSig_one_bit(SWITCH[name]['PSig'])                                               # Читаем panelsig и запоминаем значение переключателя.
            reset_CmdOp()                                                                                               # Обнуляеся перед подачей команды
            write_holding_register(address=LEGS['CmdOp']['register'], value=SWITCH[name]['CmdOp'])
            if (
                Status1_before == read_status1_one_bit(SWITCH[name]['St1'])                                             # Если видем в статусе и панели, что не поменялось значение, то ошибка
                and PanelSig_before == read_PanelSig_one_bit(SWITCH[name]['PSig'])
            ):
                print_error(f'Команда {name}({description}) не сработала на {i} итерации.')
                not_error = False
                count_error += 1
        print_text_grey(f'Переключатель {name}({description}) работет исправно.') if count_error == 0 else None         # Если все итерации прошли успешно, то выдаем сообщение.
    return not_error


@writes_func_failed_or_passed
def checking_generation_messages_and_msg_off(not_error):  # Готово.
    print_title('Старт проверки включения и отключения режима генерации сообщений (командой на CmdOp).')

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
    MsgOff = read_status1_one_bit(SWITCH['MsgOff']['St1'])
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
            MsgOff = read_status1_one_bit(SWITCH['MsgOff']['St1'])
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
    print_title('Старт проверки формирования кода 20001 при записи некорректной команды на CmdOp.')
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


@writes_func_failed_or_passed
def cheking_on_off_AlarmOff(not_error):  # Готово. Возможно требует доработки проверки на все уставки, а не на одну.
    print_title('Старт проверки работоспособности AlarmOff.')

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
    print_title('Старт проверки возможности включения режимов командой на CmdOp.')
    # Создаем словарь для проверки с наименованиями команд режимов и сообщений при переходе на данные режимы.
    data = {
        'Oos':   {'PanelSig': 1,  'messages': [20100]},
        'Imit':  {'PanelSig': 2,  'messages': [2, 51, 20200]},
        'Tst':   {'PanelSig': 4,  'messages': [5, 52, 20500]},
        'Fld':   {'PanelSig': 3,  'messages': [4, 55, 20400]},
        'Imit1': {'PanelSig': 2,  'messages': [2, 54, 20200]},
    }
    Imit1 = 0  # переменная для получения значений при втором проходе Imit1.
    # Перебираем в цикле команды для включения режимов (Oos, Imit, Tst, Fld, Imit).
    for command in ('Oos', 'Imit', 'Tst', 'Fld', 'Imit'):

        # Читаем сообщения, записываем в переменную и сортируем. Подаем команду на запись на ножку CmdOp.
        old_messages = read_all_messages()
        write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP[command])

        # Каждый проход через 'Imit' увеличиваем Imit1 на 1.
        Imit1 += 1 if command == 'Imit' else 0

        # Читаем новые сообщения, status1 и PanelSig.
        new_messages = read_new_messages(old_messages)
        new_messages.sort()
        status1 = read_status1_one_bit(STATUS1[command])
        PanelSig = read_PanelMode()

        # Если это второй проход через 'Imit', то меняем command.
        command = 'Imit1' if Imit1 == 2 else command

        # Проверяем активацию режимов по сообщениям, status1 и PanelSig. Если соответствуют ожидаемым
        # значениям из словаря data, то проверка пройдена.
        if new_messages == data[command]['messages'] and status1 is True and PanelSig == data[command]['PanelSig']:
            print_text_grey(f'Режим {command} успешно активирован. Проверка пройдена.')
        else:
            print_error(f'Ошибка! Режим {command} не активирован. {new_messages}')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_signal_transfer_low_level_on_middle_level(not_error):  # Готово.
    print_title('Проверка прохождения сигнала с нижнего уровня на средний и правильности пересчета.')

    # Создаем вспомогательные переменные со значениями для записи (Input) и сравнения (Out и OutmA).
    Input_list = [-9999.9,  -100.1,    0.0,  4.0,  11.95,  20.0,    88.91,   100.0,  555.67,    9876.12345, 12.0]
    OutmA_list = [-9999.9,  -100.1,    0,  4.0,  11.95,    20.0,    88.91,   100.0,    555.67,    9876.123, 12.0]
    Out_list = [-62524.379, -650.625, -25,  0,   49.688,   100.0,   530.688,   600,    3447.938,  61700.77, 50]

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
            print_error(f'Значение {Input_list[i]} пересчиталось некорректно. Out={Out}, а ожидалось {Out_list[i]}.')
            not_error = False
        elif OutmA != OutmA_list[i]:
            print_error(f'Значение {Input_list[i]} пересчиталось некорректно. Out={OutmA}, а ожидалось {OutmA_list[i]}.')
            not_error = False
        elif error is True:
            print_error(f'Ошибка записи значения {Input_list[i]} в Input.')
            not_error = False
    return not_error


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


@writes_func_failed_or_passed
def checking_not_impossible_min_more_max(not_error):  # Готово.
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
def checking_errors_channel_module_sensor_and_external_error(not_error):  # Готово.
    print_title('Проверка сработки ошибок канала, модуля, сенсора и внешней ошибки.')

    # Создаем словарь с данными для проверки. Ключи - ошибки, знач. списки значений сообщений.
    data = {
        'ChFlt':    {'bit': 0, 'msg_by_True': [204, 212], 'msg_by_False': [111, 254, 262]},
        'ModFlt':   {'bit': 1, 'msg_by_True': [206, 212], 'msg_by_False': [111, 256, 262]},
        'SensFlt':  {'bit': 2, 'msg_by_True': [208, 212], 'msg_by_False': [111, 258, 262]},
        'ExtFlt':   {'bit': 3, 'msg_by_True': [210, 212], 'msg_by_False': [111, 260, 262]}
    }

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

        # Читаем сообщения и отсортировываем, создаем счетчик ошибок.
        new_messages = read_new_messages(old_message)
        new_messages.sort()
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

        # Читаем сообщения и отсортировываем, обнуляем счетчик ошибок.
        new_messages = read_new_messages(old_message)
        new_messages.sort()
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

        # Ждем 1 секунду, чтобы функции доделали свою работу.
        sleep(1)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking(not_error):  # Готово.
    print_title('Проверка.')
    return not_error


@start_with_limits_values
@running_time
@connect_and_close_client
def main():
    checking_errors_writing_registers()
    cheking_on_off_for_cmdop()
    checking_generation_messages_and_msg_off()
    cheking_incorrect_command_cmdop()
    cheking_on_off_AlarmOff()
    checking_operating_modes()
    checking_signal_transfer_low_level_on_middle_level()
    checking_write_maxEV_and_minEV()
    checking_not_impossible_min_more_max()
    checking_errors_channel_module_sensor_and_external_error()
    checking()




if __name__ == "__main__":
    main()











