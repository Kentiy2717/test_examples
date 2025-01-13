from time import sleep
from assist_function_FB_DPcc import check_work_kvitir_off, check_work_kvitir_on, switch_position, switch_position_for_legs, turn_on_mode
from constants_FB_DPcc import BAD_REGISTER, CMDOP, CMDOP_REGISTER, INPUT_REGISTER, OUT_REGISTER, PANELSIG, PANELSTATE, START_VALUE, STATUS1, STATUS2, SWITCH, VALUE_UNRELIABILITY
from probably_not_used.constants import DETAIL_REPORT_ON
from func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from common_read_and_write_functions import (
    read_coils,
    read_discrete_inputs,
    this_is_write_error,
    write_coil,
    write_holding_register,
    read_float,
    write_holding_registers,
    write_holding_registers_int
)
from read_and_write_functions_FB_DPcc import write_CmdOp
from read_messages import read_all_messages, read_new_messages
from common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from read_stutuses_and_message_FB_DPcc import read_PanelAlm_one_bit, read_PanelMode, read_PanelSig_one_bit, read_PanelState, read_status1_one_bit, read_status2_one_bit
from wrappers_FB_DPcc import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
# Проверка ошибок при записи c нулевым, отрицательными и положительными значениями.
def checking_errors_writing_registers(not_error):
    print_title('Проверка ошибок при записи c нулевым и положительными значениями')

    # Создаем словарь с регистрами и значениями.
    data = {
        'Input':     {'register': START_VALUE['Input']['register'],       'values': (-4.1, 0.0, 22.0)},
        'DeltaV':    {'register': START_VALUE['DeltaV']['register'],      'values': (-4.1, 0.5, 0.0)},
        'Period':    {'register': START_VALUE['Period']['register'],      'values': (-4,   0,   100)},
        'MaxEV':     {'register': START_VALUE['MaxEV']['register'],       'values': (2.1,  0.0, 99.9, -23.5)},
        'MinEV':     {'register': START_VALUE['MinEV']['register'],       'values': (0.0, -10.1, 9.9, -123.5)},
        'T01':       {'register': START_VALUE['T01']['register'],         'values': (-4,   0,   1000)},
        'AHLim':     {'register': START_VALUE['AHLim']['register'],       'values': (-99.9, 0.0, 89.7)},
        'WHLim':     {'register': START_VALUE['WHLim']['register'],       'values': (-89.9, 0.0, 89.7)},
        'Hyst':      {'register': START_VALUE['Hyst']['register'],        'values': (-4.1, 0.0, 1.5)},
        'Alarm_Off': {'register': START_VALUE['Alarm_Off']['register'],   'values': (True, False)},
        'ChFlt':     {'register': START_VALUE['ChFlt']['register'],       'values': (True, False)},
        'ModFlt':    {'register': START_VALUE['ModFlt']['register'],      'values': (True, False)},
        'SensFlt':   {'register': START_VALUE['SensFlt']['register'],     'values': (True, False)},
        'ExtFlt':    {'register': START_VALUE['ExtFlt']['register'],      'values': (True, False)},
        'WHLimEn':   {'register': START_VALUE['WHLimEn']['register'],     'values': (True, False)},
        'AHLimEn':   {'register': START_VALUE['AHLimEn']['register'],     'values': (True, False)},
        'CmdOp':     {'register': START_VALUE['CmdOp']['register'],       'values': (-4,   0, 4)},
    }
    # Проходимся циклом по всем регистрам и значениям для записии. Создаем переменные для проверки.
    for name, reg_and_vals in data.items():
        register = reg_and_vals['register']
        values = reg_and_vals['values']
        for num in range(0, len(values)):
            value = values[num]
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
# Проверка работы переключателей (командой на CmdOp).
def cheking_on_off_for_cmdop(not_error):
    print_title('Проверка работы переключателей (командой на CmdOp).')

    # Проходим циклом по всем переключателям. Пытаемся включить и выключить каждый 4 раза.
    for command in SWITCH:
        required_bool_value = True
        count_error = 0
        for iter in range(4):

            # Читаем Status1 и PanelSig и запоминаем значение переключателя.
            st1_before = read_status1_one_bit(number_bit=STATUS1[command])
            PanelSig_before = read_PanelSig_one_bit(number_bit=PANELSIG[command])
            switch_position(command=command, required_bool_value=required_bool_value)

            # Если видем в статусе или панели, не поменялось значение, то ошибка.
            if (
                st1_before == read_status1_one_bit(number_bit=STATUS1[command])                                             # Если видем в статусе и панели, что не поменялось значение, то ошибка
                or PanelSig_before == read_PanelSig_one_bit(number_bit=PANELSIG[command])
            ):
                print_error(f'Команда {command} не сработала на {iter} итерации.')
                not_error = False
                count_error += 1

            # Переключаем значение. Если счетчик ошибок нулевой, то выводим сообщение.
            required_bool_value = not required_bool_value
        print_text_grey(f'Переключатель {command} работет исправно.') if count_error == 0 else None         # Если все итерации прошли успешно, то выдаем сообщение.
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_generation_messages_and_msg_off(not_error):  # Готово.
    print_title('Проверка включения и отключения режима генерации сообщений (командой на CmdOp).')
    print_error('ОШИБКА ПО ПРИЧИНЕ ТОГО, ЧТО БАГ. СООБЩЕНИЯ НЕ ДОЛЖНЫ ФОРМИРОВАТЬСЯ.')

    # Убеждаемся, что генерация сообщений и аварийная уставка включены. Получаем значение уставки.
    switch_position(command='MsgOff', required_bool_value=False)
    switch_position(command='AHLimEn', required_bool_value=True)
    AHLim_val = read_float(address=START_VALUE['AHLim']['register'])

    # Убеждаемся, что значение АП меньше уставки. Если Out >= AHLim, то выводим ошибку.
    if read_float(address=OUT_REGISTER) >= AHLim_val:
        print_error(
            'Тест не может быть выполнен. Проверьте тест №1. Ошибка записи значений в предыдущих тестах.'
        )
        not_error = False

    # Читаем сообщения. Устанавливаем значение Input выше уставки (Input > AHLim).
    old_messages = read_all_messages()
    write_holding_registers(address=INPUT_REGISTER, values=(AHLim_val + 1))

    # Получаем значение MsgOff и AHAct в статус1.
    MsgOff = read_status1_one_bit(STATUS1['MsgOff'])
    AHAct = read_status1_one_bit(STATUS1['AHAct'])

    # Если уставка сработала и сообщения сформировались, то выводим сообщение и проверяем дальше.
    if AHAct is True and read_new_messages(old_messages) != []:
        print_text_grey(f'Сообщение о превышении аварийной уставки сформировано. При MsgOff={MsgOff}')

        # Снимаем сигнал уставки. Обновляем значение AHLimEn в статус1.
        write_holding_registers(address=INPUT_REGISTER, values=(AHLim_val - 1))
        AHAct = read_status1_one_bit(STATUS1['AHAct'])

        # Если аварийный сигнал снят, то продолжаем проверку.
        if AHAct is False:

            # Отключаем генерацию сообщений. Читаем сообщения.
            switch_position(command='MsgOff', required_bool_value=True)
            old_messages = read_all_messages()

            # Устанавливаем  значение в Input выше уставки. Получаем значение AHAct из статус1.
            write_holding_registers(address=INPUT_REGISTER, values=(AHLim_val + 1))
            AHAct = read_status1_one_bit(STATUS1['AHAct'])

            # Если уставка сработала и сообщение не формируется, то проверка пройдена.
            if AHAct is True and read_new_messages(old_messages) == []:
                print_text_grey(f'Сообщение о превышении аварийной уставки не сформировано. При MsgOff={MsgOff}')
            else:
                Out = read_float(address=OUT_REGISTER)
                print_error(
                    f'Сообщение о превышении аварийной уставки сформировалось при MsgOn={MsgOff}. '
                    f'Дальнейшие тесты нецелесообразны. (AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
                )
                not_error = False
        else:
            Out = read_float(address=OUT_REGISTER)
            print_error(
                'Аварийная уставка не снимается. Дальнейшие тесты нецелесообразны. '
                f'(MsgOn={MsgOff}, AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
            )
            not_error = False
    else:
        Out = read_float(address=OUT_REGISTER)
        print_error(
            'Сообщение о превышении аварийной уставки не формируется. Дальнейшие тесты нецелесообразны. '
            f'(MsgOn={MsgOff}, AHAct={AHAct}, Out={Out}, AHLim={AHLim_val}).'
        )
        not_error = False

    # Меняем режим и снова проверяем.
    switch_position(command='MsgOff', required_bool_value=True)
    old_messages = read_all_messages()
    write_CmdOp(command='Imt1')
    new_messages = read_new_messages(old_messages)
    if new_messages != []:
        print_error('Ошибка! Сообщение о принятии команды оператора об активации '
                    'режима "Imt1" сформировано при MsgOff=True.')
        not_error = False
    else:
        print_text_grey('Проверка пройдена. Сообщение об активации режима "Imit" не сформировалось при MsgOff=True.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка формирования кода 20001 при записи некорректной команды на CmdOp.
def cheking_incorrect_command_cmdop(not_error):
    print_title('Проверка формирования кода 20001 при записи некорректной команды на CmdOp.')
    for command in [900, 949, 999]:
        old_messages = read_all_messages()
        write_holding_register(address=CMDOP_REGISTER, value=command)
        new_messages = read_new_messages(old_messages)
        if 20001 in new_messages:
            print_text_grey(f'При передачи команды {command} на CmdOp сформирован ожидаемый код сообщения - 20001.')
        else:
            print_error(f'При передачи команды {command} на CmdOp сформирован код сообщения отличный от ожидаемого. '
                        f'message={new_messages}')
            not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка возможности включения режимов командой на CmdOp.
def checking_operating_modes(not_error):
    print_title('Проверка возможности включения режимов командой на CmdOp.')
    # Создаем словарь для проверки с наименованиями команд режимов и сообщений при переходе на данные режимы.
    data = {
        'Oos':   {'PanelMode': 1,  'messages': [20100]},
        'Imt2':  {'PanelMode': 4,  'messages': [30, 51, 23000]},
        'Imt1':  {'PanelMode': 3,  'messages': [3, 80, 20300]},
        'Imt0':  {'PanelMode': 2,  'messages': [2, 53, 20200]},
        'Fld':   {'PanelMode': 5,  'messages': [4, 52, 20400]},
        'Tst':   {'PanelMode': 6,  'messages': [5, 54, 20500]},
        'Imit2': {'PanelMode': 4,  'messages': [30, 55, 23000]},
    }
    Imit2 = 0  # переменная для получения значений при втором проходе Imt2.
    # Перебираем в цикле команды для включения режимов (Oos, Imit, Tst, Fld, Imit).
    for command in ('Oos', 'Imt2', 'Imt1', 'Imt0', 'Fld', 'Tst', 'Imt2'):

        # Читаем сообщения, записываем в переменную и сортируем. Подаем команду на запись на ножку CmdOp.
        old_messages = read_all_messages()
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])

        # Каждый проход через 'Imit' увеличиваем Imit1 на 1.
        Imit2 += 1 if command == 'Imt2' else 0

        # Читаем новые сообщения, status1 и PanelMode.
        new_messages = read_new_messages(old_messages)
        new_messages.sort()
        status1 = read_status1_one_bit(number_bit=STATUS1[command])
        PanelMode = read_PanelMode()

        # Если это второй проход через 'Imt2', то меняем command.
        command = 'Imit2' if Imit2 == 2 else command

        # Проверяем активацию режимов по сообщениям, status1 и PanelMode. Если соответствуют ожидаемым
        # значениям из словаря data, то проверка пройдена.
        if new_messages == data[command]['messages'] and status1 is True and PanelMode == data[command]['PanelMode']:
            print_text_grey(f'Режим {command} успешно активирован. Проверка пройдена.')
        else:
            not_error = False
            print_error(f'Ошибка! Режим {command} не активирован. {new_messages}')
            if new_messages != data[command]['messages']:
                print_error(f'Пришло {new_messages}, а ожидалось {data[command]["messages"]}.')
            if status1 is False:
                print_error(f'Значение status1={status1}, а ожидалось True.')
            if PanelMode != data[command]['PanelMode']:
                print_error(f'В PanelMode пришло - {PanelMode}, а ожидалось {data[command]["PanelMode"]}.')
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка установки команд с разных панелей управления.
def checking_the_installation_of_commands_from_different_control_panels(not_error):
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


@reset_initial_values
@writes_func_failed_or_passed
# Проверка работоспособности квитирования. Возникновение при переходе через уставку.
def checking_kvitir(not_error):
    print_title('Проверка работоспособности квитирования. Возникновение при переходе через уставку.')

    # Создаем словарь для проверки.
    data = {
        'WHLim': {'kvit_on': [113], 'kvit_off': [23100]},
        'AHLim': {'kvit_on': [114], 'kvit_off': [23100]}
    }

    # Включаем уставки. Провереяем, что квитирование не требуется.
    for command in ('WHLimEn', 'AHLimEn'):
        write_CmdOp(command=command)
    old_messages = read_all_messages()
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[])
    if not_error is False:
        print_error('Квитирование не сбросилось в декораторе reset_initial_values. '
                    'Дальнейшее тестирование нецелесообразно.')
        return not_error

    # В цикле проверяем сработку и снятие квитирования при переходе через уставки.
    for setpoint, msg in data.items():
        print_text_white(f'\nПроверка сработки квитировании при прохождении уставки {setpoint}.')

        # Читаем сообщения. Переключаем Input > уставки. Проверяем включение сигнала "Требуется квитирование".
        old_messages = read_all_messages()
        write_holding_registers(address=INPUT_REGISTER, values=(START_VALUE[setpoint]['start_value'] + 1))
        not_error = check_work_kvitir_on(old_messages=old_messages, not_error=not_error, msg=msg['kvit_on'])

        # Читаем сообщением и снимаем сигнал "Требуется квитирование" командой на CmdOp.
        # Проверяем отключение сигнала "Требуется квитирование".
        old_messages = read_all_messages()
        write_CmdOp(command='Kvitir')
        not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=msg['kvit_off'])

    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_off_messages_and_statuses_and_kvitir_in_masking_mode(not_error):  # Делаю.
    print_title('Проверка отсутствия генерации сообщений и статусов, в режиме "Маскирование".')

    # Включаем режим "Маскирование". Читаем сообщения. Устанавливаем сигнал недостоверности.
    not_error = turn_on_mode(mode='Oos')
    old_messages = read_all_messages()
    write_coil(address=START_VALUE['ExtFlt']['register'], value=True)

    # Читаем сообщения, статусы и ножку Bad, бит квитирования. Выполняем проверку.
    new_messages = read_new_messages(old_messages)
    st1 = read_status1_one_bit(number_bit=STATUS1['Bad'])
    st1_kvit = read_status1_one_bit(number_bit=STATUS1['Kvitir'])
    st2 = read_status2_one_bit(number_bit=STATUS2['ExtFlt'])
    PanelAlm = read_PanelAlm_one_bit(number_bit=STATUS2['ExtFlt'])
    PanelState = read_PanelState() == PANELSTATE['Oos']
    Bad = read_discrete_inputs(address=BAD_REGISTER, bit=0)
    if new_messages == [] and PanelState and (st1 and st2 and PanelAlm and Bad and st1_kvit) is False:
        print_text_grey('Проверка отсутствия генерации сообщений и статусов, в режиме "Маскирование" прошла успешно.')
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
# Проверка на непрохождении сигнала недостоверности значения DP при неисправности
# модуля, канала, датчика и внешней ошибке в режимах "Имитация2", "Имитация1", "Имитация0", "Маскирование".
def checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking(not_error):
    print_title('Проверка на непрохождении сигнала недостоверности значения DP при '
                'неисправности модуля, канала, датчика и внешней ошибке '
                'в режимах "Имитация2", "Имитация1", "Имитация0", "Маскирование".')

    # Проходим циклом по всем режимам работы (кроме режима "Fld"), включаем поочередно и тестируем.
    for mode in ('Oos', 'Imt2', 'Imt1', 'Imt0'):
        turn_on_mode(mode=mode)
        print_text_white(f'\nПроверка в режиме {mode}.')

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
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка сработки ошибок канала, модуля, сенсора и внешней ошибки.
def checking_errors_channel_module_sensor_and_external_error_fld_and_tst(not_error):
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
        print_text_white(f'\nПроверка в режиме {mode}.')

        # Проходим по значениям словаря с наименованием ошибок.
        for name, msg in data.items():

            # ПРОВЕРКА ВКЛЮЧЕНИЯ.
            # Читаем сообщения выбираем какой бит смотреть в status2 и PanelAlm.
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
# Проверка задержки на срабатывание в режимах Fld, Tst, Imt0, Imt1, Imt2.
def checking_t01(not_error):
    print_title('Проверка задержки на срабатывание в режимах Fld, Tst, Imt0, Imt1, Imt2.')

    # Включаем уставки. Провереяем, что квитирование не требуется.
    for command in ('WHLimEn', 'AHLimEn'):
        write_CmdOp(command=command)
    old_messages = read_all_messages()
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[])
    if not_error is False:
        print_error('Квитирование не сбросилось в декораторе reset_initial_values. '
                    'Дальнейшее тестирование нецелесообразно.')
        return not_error

    # Меняем режимы в цикле. Устанавливаем значение Т01 = 1 сек и меняем значение Input. Ждем 0,5сек.
    for mode in ('Fld', 'Imt0', 'Imt1', 'Imt2', 'Tst'):
        not_error = turn_on_mode(mode=mode)
        print_text_white(f'Проверка в режиме {mode}.')
        write_holding_registers_int(address=START_VALUE['T01']['register'], values=1000)

        # Создаем функцию для проверки, которая квитирует, меняет параметр АП(value), ждет(sleep_time) и проверяет st1.
        def checking(sleep_time, msg, required_bool_value, not_error=not_error, mode=mode):
            sleep(sleep_time)
            number_bit = STATUS1['AHAct'] if mode != 'Imt1' else STATUS1['WHAct']
            number_bit_kvitir = STATUS1['Kvitir']
            st1 = read_status1_one_bit(number_bit=number_bit)
            st1_kvitir = read_status1_one_bit(number_bit=number_bit_kvitir)
            if (st1 and st1_kvitir) is required_bool_value:
                print_text_grey(f'Проверка {msg}, через {sleep_time}сек при T01=1сек '
                                'прошла успешно.')
            else:
                not_error = False
                if st1 is not required_bool_value:
                    print_error(f'Ошибка проверки {msg}, через {sleep_time}сек при T01=1сек.\n'
                                f'В Status1 в бите №{number_bit} - {st1}, а ожидалось {required_bool_value}.')
                elif st1_kvitir is not required_bool_value:
                    print_error(f'Ошибка проверки {msg}, через {sleep_time}сек '
                                f'при T01 = 1сек.\nВ Status1 в бите №{number_bit_kvitir} - {st1}, '
                                f'а ожидалось {required_bool_value}.')
            return not_error

        # Если текущий режим из списка, то выставляем значение Input выше уставок.
        # Проверяем несработку уставки через 0,5 сек.
        if mode in ('Fld', 'Tst', 'Imt0'):
            write_holding_registers(address=INPUT_REGISTER, values=(START_VALUE['AHLim']['start_value'] + 1))
        not_error = checking(
            sleep_time=0.5,
            msg='несработки уставки при ее превышении',
            required_bool_value=False
        )

        # Возвращаем значение АП в исходное положение и проверяем через 1,5 сек что уставка попрежнему не сработала.
        if mode in ('Fld', 'Tst', 'Imt0'):
            write_holding_registers(address=INPUT_REGISTER, values=START_VALUE['Input']['start_value'])
            required_bool_value = False
        else:
            required_bool_value = True
        not_error = checking(
            sleep_time=1.0,
            msg='несработки уставки при возвращении в исходное положение',
            required_bool_value=required_bool_value
        )

        # Опять записываем значение превышающее уставку в регистр и проверяем сработку уставки через 1 сек.
        write_holding_registers(address=INPUT_REGISTER, values=(START_VALUE['AHLim']['start_value'] + 1))
        sleep(1)
        if mode == 'Imt0':
            required_bool_value = False
        else:
            required_bool_value = True
        not_error = checking(
            sleep_time=1.0,
            msg='сработки уставки при ее превышении',
            required_bool_value=required_bool_value)

        # Возвращаем в исходное положение значение АП и квитируем.
        write_holding_registers(address=INPUT_REGISTER, values=START_VALUE['Input']['start_value'])
        write_CmdOp(command='Kvitir')
    return not_error


@running_time
# @start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ АП.
    '''

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')

    print('ОБЩИЕ ПРОВЕРКИ\n')
    # checking_errors_writing_registers()
    # cheking_on_off_for_cmdop()
    # checking_generation_messages_and_msg_off()
    # cheking_incorrect_command_cmdop()
    # checking_operating_modes()
    # checking_the_installation_of_commands_from_different_control_panels()
    # checking_kvitir()
    # checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking()
    # checking_errors_channel_module_sensor_and_external_error_fld_and_tst()
    checking_t01()


    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    # checking_off_messages_and_statuses_and_kvitir_in_masking_mode()

    # checking_()


if __name__ == "__main__":
    main()
