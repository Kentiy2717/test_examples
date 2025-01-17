import sys
import os

# Эта строка добавляет путь к корневой директории проекта в sys.path, чтобы Python мог находить модули и пакеты,
# расположенные в этом проекте, независимо от текущей директории запуска скрипта.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Включаем поддержку ANSI escape-последовательностей в консоли Windows
if sys.platform == "win32":
    os.system("")

from itertools import combinations
from time import sleep

from FB_DP.assist_function_FB_DP import (
    check_work_kvitir_off,
    check_work_kvitir_on,
    switch_position,
    switch_position_for_legs,
    turn_on_mode
)
from FB_DP.constants_FB_DP import (
    BAD_REGISTER,
    CMDOP,
    CMDOP_REGISTER,
    INPUT_REGISTER,
    OUT_REGISTER,
    PANELMODE,
    PANELSIG,
    PANELSTATE,
    START_VALUE,
    STATUS1,
    STATUS2,
    SWITCH,
    VALUE_UNRELIABILITY,
    WORK_MODES
)
from FB_DP.read_and_write_functions_FB_DP import write_CmdOp
from FB_DP.read_stutuses_and_message_FB_DP import (
    read_PanelAlm_one_bit,
    read_status1_one_bit,
    read_status2_one_bit,
    read_PanelSig_one_bit,
    read_PanelMode,
    read_PanelState
)
from FB_DP.wrappers_FB_DP import reset_initial_values
from common.constants import DETAIL_REPORT_ON
from common.func_print_console_and_write_file import (
    print_text_white,
    print_title,
    print_error,
    print_text_grey,
)
from common.common_read_and_write_functions import (
    read_discrete_inputs,
    this_is_write_error,
    write_coil,
    write_holding_register,
    read_float,
    write_holding_registers_int
)
from common.read_messages import read_all_messages, read_new_messages
from common.common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)


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
    print_error('ОШИБКА ПО ПРИЧИНЕ ТОГО, ЧТО БАГ. СООБЩЕНИЯ НЕ ДОЛЖНЫ ФОРМИРОАТЬСЯ.')

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
def checking_signal_transfer_low_level_on_middle_level_and_invers(not_error):
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
# Проверка отсутствия генерации сообщений и статусов, в режиме "Маскирование".
def checking_off_messages_and_statuses_and_kvitir_in_masking_mode(not_error):
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
    print_error('ОШИБКА ПО ПРИЧИНЕ ТОГО, ЧТО ДОЛЖНО БЫТЬ 21900, А НЕ 21000.')

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
# Проверка корректности значений в режиме «Имитация 1» и «Имитация 0» при изменении в Input и включения инверсии.
def checking_checking_imit1_and_imit0(not_error):
    print_title('Проверка корректности значений в режиме «Имитация 1» и «Имитация 0» '
                'при изменении в Input и включения инверсии.')

    # Создаем вспомогательную функцию для проверки.
    def check_imit1_and_imit0(value, not_error):

        # Устанавливаем Input в value. Считываем Out и проверяем соответствие режиму.
        write_coil(address=INPUT_REGISTER, value=value)
        Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
        if Out is True and mode == 'Imt1':
            print_text_grey(f'В режиме {mode}(Имитация 1) при изменении Input в {value}, Out = {Out}. '
                            'Проверка прошла успешно.')
        elif Out is False and mode == 'Imt0':
            print_text_grey(f'В режиме {mode}(Имитация 0) при изменении Input в {value}, Out = {Out}. '
                            'Проверка прошла успешно.')
        else:
            not_error = False
            print_error(f'Ошибка! В режиме {mode} при изменении Input в {value}, Out = {Out}.')
        return not_error

    # Проходим в цикле по режимам "Имитация 1" и "Имитация 0".
    for mode in ('Imt1', 'Imt0'):
        not_error = turn_on_mode(mode=mode)

        # Проверяем при Input = True.
        not_error = check_imit1_and_imit0(value=True, not_error=not_error)

        # Проверяем при Input = False.
        not_error = check_imit1_and_imit0(value=False, not_error=not_error)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка на непрохождении сигнала недостоверности значения DP при неисправности
# модуля, канала, датчика и внешней ошибке в режимах "Имитация1", "Имитация0", "Маскирование".
def checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking(not_error):
    print_title('Проверка на непрохождении сигнала недостоверности значения DP при '
                'неисправности модуля, канала, датчика и внешней ошибке. '
                'в режимах "Имитация1", "Имитация0", "Маскирование".')

    # Проходим циклом по всем режимам работы (кроме режима "Fld"), включаем поочередно и тестируем.
    for mode in ('Oos', 'Imt1', 'Imt0'):
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
        'ChFlt':    {'bit': 0, 'msg_by_True': [204], 'msg_by_False': [254]},
        'ModFlt':   {'bit': 1, 'msg_by_True': [206], 'msg_by_False': [256]},
        'SensFlt':  {'bit': 2, 'msg_by_True': [208], 'msg_by_False': [258]},
        'ExtFlt':   {'bit': 3, 'msg_by_True': [210], 'msg_by_False': [260]}
    }

    # Проверяем в цикле режим "Полевая обработка" и "Тестирование".
    for mode in ('Fld', 'Tst'):
        turn_on_mode(mode=mode)
        print_text_white(f'\nПроверка в режиме {mode}.')

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
# Проверка задержки на срабатывание в режимах Fld, Tst, Imit.
def checking_t01(not_error):
    print_title('Проверка задержки на срабатывание в режимах Fld, Tst, Imt0 Imt1.')
    print_error('ТЕСТ НЕ ПРОХОДИТ, ПОТОМУ ЧТО Tst РАБОТАЕТ НЕ ВЕРНО СМОТРИ ДЕБАГ!.')

    # Провереяем, что квитирование не требуется.
    old_messages = read_all_messages()
    not_error = check_work_kvitir_off(old_messages=old_messages, not_error=not_error, msg=[])
    if not_error is False:
        print_error('Квитирование не сбросилось в декораторе reset_initial_values. '
                    'Дальнейшее тестирование нецелесообразно.')
        return not_error

    # Проходим по режимам в цикле. Устанавливаем значение Т01 = 1 сек.
    for mode in ('Imt1', 'Imt0', 'Fld', 'Tst'):

        if mode == 'Imt0':
            write_coil(address=INPUT_REGISTER, value=True)

        # Устанавливаем значение Т01 = 1 сек. Меняем режим.
        print_text_white(f'Проверка в режиме {mode}.')
        write_holding_registers_int(address=START_VALUE['T01']['register'], values=1000)
        not_error = turn_on_mode(mode=mode)

        # Создаем функцию для проверки, которая квитирует, меняет параметр АП(value), ждет(sleep_time) и проверяет st1.
        def checking(sleep_time, msg, required_bool_value, not_error=not_error, mode=mode):
            sleep(sleep_time)
            number_bit = STATUS1['DP_Act'] if mode != 'Imt0' else STATUS1['DP_Inact']
            number_bit_kvitir = STATUS1['Kvitir']
            st1 = read_status1_one_bit(number_bit=number_bit)
            st1_kvitir = read_status1_one_bit(number_bit=number_bit_kvitir)
            Out = read_discrete_inputs(address=OUT_REGISTER, bit=0)
            if (sleep_time < 1.0 and mode == 'Imt0') or (sleep_time >= 1.0 and mode in ('Imt1', 'Fld')):
                expected_Out = True
            else:
                expected_Out = False
            if (st1 and st1_kvitir) is required_bool_value and Out == expected_Out:
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
                elif Out != expected_Out:
                    print_error(f'Ошибка проверки {msg}, через {sleep_time}сек при T01=1сек.\n'
                                f' - В Out - {Out}, а ожидалось {expected_Out}.')
            return not_error

        # Если текущий режим из списка, то выставляем значение Input выше уставок.
        # Проверяем несработку уставки через 0,5 сек.
        if mode in ('Fld', 'Tst'):
            write_coil(address=INPUT_REGISTER, value=True)
            required_bool_value = False
        not_error = checking(
            sleep_time=0.5,
            msg='неизменения DP при изменении Input',
            required_bool_value=False
        )

        # Возвращаем значение DP в исходное положение и проверяем через 1,5 сек что уставка попрежнему не сработала.
        if mode == 'Tst':
            write_coil(address=INPUT_REGISTER, value=False)
            required_bool_value = False
        else:
            required_bool_value = True
        not_error = checking(
            sleep_time=1.0,
            msg='неизменения DP при возвращении Input в исходное положение',
            required_bool_value=required_bool_value
        )

        # Опять меняем значение DP и проверяем сработку через 1 сек.
        if mode == 'Fld':
            required_bool_value = True
        elif mode == 'Tst':
            required_bool_value = False
        write_coil(address=INPUT_REGISTER, value=True)
        sleep(1)
        not_error = checking(
            sleep_time=1.0,
            msg='изменения DP при изменении Input',
            required_bool_value=required_bool_value
        )

        # Возвращаем в исходное положение значение DP и квитируем.
        write_holding_registers_int(address=START_VALUE['T01']['register'], values=0)
        not_error = turn_on_mode(mode='Fld')
        write_coil(address=INPUT_REGISTER, value=False)
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
def checking_switching_between_modes_in_case_of_errors(not_error):
    print_title('Проверка возможности перехода из режима "Маскирование" в другие режимы при неисправностях \n'
                'канала, модуля, сенсора,внешней ошибки.')
    # print_error('НЕПРОХОДИТ ПОТОМУ ЧТО НУЖНЫ ОШИБКИ 201 И 203 (СМОТРИ В ДЕБАГЕ)')

    # Подготавливаем список возможных ошибок.
    switches = [('ChFlt', [204]), ('ModFlt', [206]), ('SensFlt', [208]),
                ('ExtFlt', [210])]
    work_modes_and_message = (('Imt1', [2, 108, 51, 20200]), ('Imt0', [3, 158, 51, 20300]),
                              ('Fld', [4, 51, 20400]), ('Tst', [5, 51, 20500]))

    # Перебираем все возможные комбинации от 1 до 4 одновременных ошибок.
    for r in range(1, 5):
        # В цикле перебираем возможные комбинации ошибок.
        for combo_error in combinations(switches, r):

            # Переходим в режим Oos на старте, выключаем ошибки.
            not_error = turn_on_mode(mode='Oos')
            for switch, _ in switches:
                switch_position_for_legs(command=switch, required_bool_value=False)

            #  Активируем эти ошибки, пробуем переключать режимы и проверяем меняются ли по st1 и PanelMode.
            msg_all = []
            errors = []
            for error, msg_error in combo_error:
                errors.append(error)
                msg_all.extend(msg_error)
                switch_position_for_legs(command=error, required_bool_value=True)
            for mode, msg_mode in work_modes_and_message:
                msg = msg_mode.copy()
                if mode == 'Imt1' or mode == 'Imt0':
                    st1_kvit_original = True
                else:
                    msg.extend(msg_all)
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
# Проверка неизменности значений Period, T01,
# а также сохранения положения переключателей (MsgOff, Invers) при переключениях между режимами.
def checking_values_when_switching_modes(not_error):
    print_title('Проверка неизменности значений Period, T01, а также сохранения положения \n'
                'переключателей (MsgOff, Invers) при переключениях между режимами.')

    # Создаем переменную с кортежем из всех параметров для проверки.
    params_for_check = ('Period', 'T01')

    # Создаем вспомогательную функцию для формирования словаря значений параметров и переключателей.
    def get_checklist():
        checklist = [(param, read_float(address=START_VALUE[param]['register'])) for param in params_for_check]
        checklist.extend(
            [(name, read_status1_one_bit(number_bit=STATUS1[name])) for name in SWITCH]
        )
        return checklist

    # Создаем вспомогательную функцию для проверки.
    def base_check(not_error):

        # Проходим двойным циклом по кортежу с командами для переключения в разные режимы.
        for mode1 in ('Fld', 'Tst', 'Oos', 'Imt1', 'Imt0'):
            for mode2 in ('Fld', 'Tst', 'Oos', 'Imt1', 'Imt0'):

                # Если они совпадают, то не проводим проверку.
                if mode1 == mode2:
                    continue

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
    for command in SWITCH:
        switch_position(command=command, required_bool_value=True)
    print_text_white('Старт проверки с пеерключателями в положении True.')
    not_error = base_check(not_error=not_error)
    return not_error


@running_time
# @start_with_limits_values
@connect_and_close_client
def main():
    '''
    Главная функция для запуска тестов ФБ DP.
    '''

    print('СТАРТ ТЕСТИРОВАНИЯ ФБ DP\n')

    print('ПРОВЕРКА РЕЖИМА "ПОЛЕВАЯ ОБРАБОТКА"\n')
    checking_kvitir()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')
    checking_checking_imit1_and_imit0()

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    checking_off_messages_and_statuses_and_kvitir_in_masking_mode()

    print('ОБЩИЕ ПРОВЕРКИ\n')
    checking_errors_writing_registers()
    cheking_on_off_for_cmdop()
    checking_generation_messages_and_msg_off()
    cheking_incorrect_command_cmdop()
    checking_operating_modes()
    checking_signal_transfer_low_level_on_middle_level_and_invers()
    checking_the_installation_of_commands_from_different_control_panels()
    checking_errors_channel_module_sensor_and_external_error_in_simulation_mode_and_masking()
    checking_errors_channel_module_sensor_and_external_error_fld_and_tst()
    checking_t01()
    checking_values_when_switching_modes()
    checking_switching_between_modes_in_case_of_errors()


if __name__ == "__main__":
    main()