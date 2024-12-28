import sys
from time import sleep
from assist_function_FB_DP import check_work_kvitir_off, check_work_kvitir_on, switch_position, turn_on_mode
from constants_FB_DP import BAD_REGISTER, CMDOP, CMDOP_REGISTER, INPUT_REGISTER, OUT_REGISTER, PANELSIG, PANELSTATE, START_VALUE, STATUS1, STATUS2, SWITCH, WORK_MODES
from probably_not_used.constants import DETAIL_REPORT_ON
from encode_and_decode import decode_float
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
    write_holding_registers,
    read_holding_registers,
    read_float
)
from read_and_write_functions_FB_DP import write_CmdOp
from read_messages import read_all_messages, read_new_messages
from read_stutuses_and_message_FB_DP import (
    read_PanelAlm_one_bit,
    read_status1_one_bit,
    read_status2_one_bit,
    read_PanelSig_one_bit,
    read_PanelMode,
    read_PanelState
)
from common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from wrappers_FB_DP import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
# Проверка ошибок при записи c нулевым и положительными значениями(отрицательные не предусмотрены, так как UINT).
def checking_errors_writing_registers(not_error):
    print_title('Проверка ошибок при записи c нулевым и положительными значениями'
                '(отрицательные не предусмотрены, так как UINT).')

    # Создаем словарь с регистрами и значениями.
    data = {
        'Input':       {'register': START_VALUE['Input']['register'],    'values': (True, False)},
        'ChFlt':       {'register': START_VALUE['ChFlt']['register'],    'values': (True, False)},
        'ModFlt':      {'register': START_VALUE['ModFlt']['register'],   'values': (True, False)},
        'SensFlt':     {'register': START_VALUE['SensFlt']['register'],  'values': (True, False)},
        'ExtFlt':      {'register': START_VALUE['ExtFlt']['register'],   'values': (True, False)},
        'Period':      {'register': START_VALUE['Period']['register'],   'values': (0, 100)},
        'T01':         {'register': START_VALUE['T01']['register'],      'values': (0, 1000)},
        'CmdOp':       {'register': START_VALUE['CmdOp']['register'],    'values': (0, 4)},
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
# Проверка включения и отключения режима генерации сообщений (командой на CmdOp).
def checking_generation_messages_and_msg_off(not_error):
    print_title('Проверка включения и отключения режима генерации сообщений (командой на CmdOp).')

    # Убеждаемся, что генерация сообщений отключена.
    switch_position(command='MsgOff', required_bool_value=False)
    write_coil(address=INPUT_REGISTER, value=False)

    # Создаем функцию для проверки записи в Out. Если Out != required_bool_value, то выводим ошибку.
    def check_out(required_bool_value, not_error=not_error):
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out is not required_bool_value:
            print_error(
                'Тест не может быть выполнен. Проверьте тест "checking_errors_writing_registers". '
                'Ошибка записи значений в предыдущих тестах.'
            )
            not_error = False
        return not_error

    # Убеждаемся, что значение АП False. Читаем сообщения. Устанавливаем в Input значение True. Проверяем в Out.
    not_error = check_out(required_bool_value=False)
    old_messages = read_all_messages()
    write_coil(address=INPUT_REGISTER, value=True)
    not_error = check_out(required_bool_value=True)

    # Читаем новые сообщения. Выполняем проверку. Если соообщения не сгенерировались, то ошибка.
    new_messages = read_new_messages(old_messages)
    if new_messages == []:
        print_error('Сообщение о сработки параметра не сформировано. Дальнейшие тесты не целесообразны.')
        not_error = False
    else:
        print_text_grey('Проверка пройдена. Сообщение о сработки параметра сформировано при MsgOff=False.')

    # Отключаем генерацию сообщений. Меняем значение в Input. Проверяем в Out. И читаем новые сообщения.
    switch_position(command='MsgOff', required_bool_value=True)
    old_messages = read_all_messages()
    write_coil(address=INPUT_REGISTER, value=False)
    not_error = check_out(required_bool_value=False)
    new_messages = read_new_messages(old_messages)

    # Если соообщения сгенерировались, то ошибка.
    if new_messages != []:
        print_error('Ошибка! Сообщение о дезактивации параметра сформировано, а не должно было сформироваться.')
        not_error = False
    else:
        print_text_grey('Проверка пройдена. Сообщение о дезактивации параметра не сформировалось при MsgOff=True.')    

    # Меняем режим и снова проверяем.
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
        'Imt1':  {'PanelMode': 2,  'messages': [2,  8, 51, 20200]},
        'Imt0':  {'PanelMode': 3,  'messages': [3, 52, 158, 20300]},
        'Fld':   {'PanelMode': 4,  'messages': [4, 53, 20400]},
        'Tst':   {'PanelMode': 5,  'messages': [5, 54, 20500]},
        'Imit1': {'PanelMode': 2,  'messages': [2,  8, 55, 20200]},
    }
    Imit1 = 0  # переменная для получения значений при втором проходе Imit1.
    # Перебираем в цикле команды для включения режимов (Oos, Imit, Tst, Fld, Imit).
    for command in ('Oos', 'Imt1', 'Imt0', 'Fld', 'Tst', 'Imt1'):

        # Читаем сообщения, записываем в переменную и сортируем. Подаем команду на запись на ножку CmdOp.
        old_messages = read_all_messages()
        write_holding_register(address=CMDOP_REGISTER, value=CMDOP[command])

        # Каждый проход через 'Imit' увеличиваем Imit1 на 1.
        Imit1 += 1 if command == 'Imt1' else 0

        # Читаем новые сообщения, status1 и PanelMode.
        new_messages = read_new_messages(old_messages)
        new_messages.sort()
        status1 = read_status1_one_bit(number_bit=STATUS1[command])
        PanelMode = read_PanelMode()

        # Если это второй проход через 'Imit', то меняем command.
        command = 'Imit1' if Imit1 == 2 else command

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
# Проверка прохождения сигнала с нижнего уровня на средний с инверсией и без на разных режимах.
def checking_checking_signal_transfer_low_level_on_middle_level_and_invers(not_error):  # .
    print_title('Проверка прохождения сигнала с нижнего уровня на средний, генерации сообщений и статусов'
                ' при переключении между режимами и включения инверсии.')

    print_error('\nТест не проходит, потому что в режиме Tst значение в Out не должно меняться при изменении Input.')

    # Создаем функцию для переключения инверсии и проверку включения по статусам и сообщения во всех режимах.
    def switch_inversion(required_bool_value, mode, not_error=not_error):

        # Создаем список ожидаемых сообщений при переключении инверсии.
        # !!!!! ТУТ НАДО 21900 вместо 21000 !!!!!
        if mode == 'Oos':
            expected_msg = [21000]
        elif mode == 'Imt1' or mode == 'Imt0':
            expected_msg = [10, 21000] if required_bool_value is True else [60, 21000]
        elif mode == 'Tst' or mode == 'Fld':
            expected_msg = [10, 58, 21000] if required_bool_value is True else [58, 60, 21000]

        # Читаем Status1 и PanelSig. Смотрим по ним в каком состоянии сейчас инверсия.
        st1 = read_status1_one_bit(number_bit=STATUS1['Invers'])
        PanelSig = read_PanelSig_one_bit(number_bit=PANELSIG['Invers'])

        # Если статусы совпадают и инверсия в значении required_bool_value, то ничего не делаем.
        if st1 == PanelSig and (st1 and PanelSig) is required_bool_value:
            return not_error
        else:
            # Если статусы не совпадают, то выводим ошибку, иначе подаем команду на CmdOp и проверяем состояние.
            if st1 != PanelSig:
                not_error = False
                print_error(f'Ошибка! Status1(10 бит={st1}) не равен PanelSig(0 бит={PanelSig}), должны быть равны.')
                return not_error
            else:
                old_messages = read_all_messages()
                write_CmdOp(command='Invers')

            # Читаем сообщения, Status1 и PanelSig. Смотрим по ним в каком состоянии сейчас инверсия.
            msg = read_new_messages(old_messages)
            st1 = read_status1_one_bit(number_bit=STATUS1['Invers'])
            PanelSig = read_PanelSig_one_bit(number_bit=PANELSIG['Invers'])

            # Если инверсия в значении required_bool_value, то ничего не делаем.
            if (st1 and PanelSig) is required_bool_value and msg == expected_msg:
                print_text_grey(f'Инверсия успешно переключена на {required_bool_value} в режиме {mode}.')
                return not_error
            else:
                not_error = False
                print_error(f'Ошибка! Инверсия не переключена в режиме {mode}.')
                if (st1 and PanelSig) is not required_bool_value:
                    print_error(f'- Status1(10 бит)={st1}, PanelSig(0 бит)={PanelSig}, '
                                f'а должны быть {required_bool_value}.')
                if msg != expected_msg:
                    print_error(f'- Ошибка! Пришло {msg}. Ожидалось - {expected_msg}.')
        return not_error

    # Устанавливаем в Input значение True. Считываем Out и сравниваем.
    write_coil(address=INPUT_REGISTER, value=True)
    Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
    if Out is False:
        not_error = False
        print_error(f'Ошибка! Сигнал с НУ не прошел на СУ. Out={Out}, а должен быть True.'
                    ' Дальнейшее тестирование нецелесообразно.')
        sys.exit()

    # Перебираем режимы и проверяем.
    for mode in WORK_MODES:

        # Переключаем режим.
        turn_on_mode(mode=mode)
        print_text_white(f'\nПроверка режима {mode}.')

        # Создаем переменную с ожидаемым результатом для каждого режима после инверсии.
        expected_Out = None
        if mode == 'Oos' or mode == 'Tst' or mode == 'Fld':
            expected_Out = Out
        elif mode == 'Imt0':
            expected_Out = False
        elif mode == 'Imt1':
            expected_Out = True

        #  Переключаем инверсию в True. Считываем Out и сравниваем.
        not_error = switch_inversion(required_bool_value=True, mode=mode, not_error=not_error)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out == expected_Out and mode != 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ. В Out ожидаемый результат.')
        elif not expected_Out == Out and mode == 'Fld':
            print_text_grey(f'Сигнал с НУ прошел на СУ в режиме {mode} и был инвертирован. В Out ожидаемый результат.')
        else:
            not_error = False
            print_error(f'Ошибка! В режиме {mode} сигнал с НУ не прошел на СУ или не был инвертирован. '
                        f'Out={Out}, а должен быть {expected_Out}.')

        # Переключаем значение Input в False. Считываем Out и сравниваем.
        write_coil(address=INPUT_REGISTER, value=False)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out == expected_Out and mode != 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ. В Out ожидаемый результат.')
        elif expected_Out == Out and mode == 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ и был инвертирован. '
                            'В Out ожидаемый результат.')
        else:
            not_error = False
            print_error(f'Ошибка! В режиме {mode} сигнал с НУ не прошел на СУ или не был инвертирован. '
                        f'Out={Out}, а должен быть {expected_Out}.')

        # Переключаем инверсию в False.  Считываем Out и сравниваем.
        not_error = switch_inversion(required_bool_value=False, mode=mode, not_error=not_error)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out == expected_Out and mode != 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ. В Out ожидаемый результат.')
        elif not expected_Out == Out and mode == 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ и был инвертирован. '
                            'В Out ожидаемый результат.')
        else:
            not_error = False
            print_error(f'Ошибка! В режиме {mode} сигнал с НУ не прошел на СУ или не был инвертирован. '
                        f'Out={Out}, а должен быть {expected_Out}.')

        # Переключаем значение Input в True. Считываем Out и сравниваем.
        write_coil(address=INPUT_REGISTER, value=True)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out == expected_Out and mode != 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ. В Out ожидаемый результат.')
        elif expected_Out == Out and mode == 'Fld':
            print_text_grey(f'В режиме {mode} сигнал с НУ не прошел на СУ и был инвертирован. '
                            'В Out ожидаемый результат.')
        else:
            not_error = False
            print_error(f'Ошибка! В режиме {mode} сигнал с НУ не прошел на СУ или не был инвертирован. '
                        f'Out={Out}, а должен быть {expected_Out}.')

        # Переключаем режим на Fld и возвращаем значение Input в True. Читаем Out.
        turn_on_mode(mode='Fld')
        write_coil(address=INPUT_REGISTER, value=True)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
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
def checking_off_messages_and_statuses_and_kvitir_in_masking_mode(not_error):  # Делаю.
    print_title('Проверка отсутствия генерации сообщений и статусов, в режиме "Маскирование".')

    # Включаем режим "Маскирование". Читаем сообщения. Устанавливаем сигнал недостоверности.
    turn_on_mode(mode='Oos')
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
# Проверка работоспособности квитирования. Возникновение при переходе через уставку.
def checking_kvitir(not_error):
    print_title('Проверка работоспособности квитирования. Возникновение при переходе через уставку.')
    # print_error('ПРОВЕРКА ТОЛЬКО НА Input. ВОЗМОЖНО ТРЕБУЕТСЯ ПРОВЕРИТЬ НА ДРУГИХ ПАРАМЕТРАХ.')

    # Провереяем, что квитирование не требуется.
    old_messages = read_all_messages()
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[])
    if not_error is False:
        print_error('Квитирование не сбросилось в декораторе reset_initial_values. '
                    'Дальнейшее тестирование нецелесообразно.')
        return not_error

    print_text_white('\nПроверка сработки квитировании при переключении Input.')

    # Читаем сообщения. Переключаем Input в True. Проверяем включение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_coil(address=INPUT_REGISTER, value=True)
    not_error = check_work_kvitir_on(old_messages=old_messages, not_error=not_error, msg=[8])

    # Читаем сообщением и снимаем сигнал "Требуется квитирование" командой на CmdOp.
    # Проверяем отключение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Kvitir')
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[23100])

    # Читаем сообщения. Переключаем Input в False. Проверяем включение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_coil(address=INPUT_REGISTER, value=False)
    not_error = check_work_kvitir_on(old_messages=old_messages, not_error=not_error, msg=[58])

    # Читаем сообщением и снимаем сигнал "Требуется квитирование" командой на CmdOp.
    # Проверяем отключение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Kvitir')
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[23100])

    # Аналогично для инверсии.
    print_text_white('\nПроверка сработки квитировании при переключении инверсии.')

    # Читаем сообщения. Переключаем Input в True. Проверяем включение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Invers')
    not_error = check_work_kvitir_on(old_messages=old_messages, not_error=not_error, msg=[8, 10, 21900])

    # Читаем сообщением и снимаем сигнал "Требуется квитирование" командой на CmdOp.
    # Проверяем отключение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Kvitir')
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[23100])

    # Читаем сообщения. Переключаем Input в False. Проверяем включение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Invers')
    not_error = check_work_kvitir_on(old_messages=old_messages, not_error=not_error, msg=[58, 60, 21900])

    # Читаем сообщением и снимаем сигнал "Требуется квитирование" командой на CmdOp.
    # Проверяем отключение сигнала "Требуется квитирование".
    old_messages = read_all_messages()
    write_CmdOp(command='Kvitir')
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[23100])

    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_(not_error):  # .
    print_title('Проверка.')



    return not_error


@running_time
# @start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ АП.
    '''

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')
    # checking_kvitir()
    # checking_()

    print('ОБЩИЕ ПРОВЕРКИ\n')
    # checking_errors_writing_registers()
    # cheking_on_off_for_cmdop()
    # checking_generation_messages_and_msg_off()
    # cheking_incorrect_command_cmdop()
    # checking_operating_modes()
    # checking_checking_signal_transfer_low_level_on_middle_level_and_invers()
    # checking_the_installation_of_commands_from_different_control_panels()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')
    # checking_()

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    checking_off_messages_and_statuses_and_kvitir_in_masking_mode()


if __name__ == "__main__":
    main()