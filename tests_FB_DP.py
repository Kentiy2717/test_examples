from time import sleep
from assist_function_FB_DP import switch_position
from constants_FB_DP import INPUT_REGISTER, OUT_REGISTER, PANELSIG, START_VALUE, STATUS1, SWITCH
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

    # Убеждаемся, что генерация сообщений и включена.
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
def checking_(not_error):  # .
    print_title('Проверка работы переключателей (командой на CmdOp).')



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
    # checking_()

    print('ОБЩИЕ ПРОВЕРКИ\n')
    # checking_errors_writing_registers()
    # cheking_on_off_for_cmdop()
    # checking_generation_messages_and_msg_off()

    print('ПРОВЕРКА РЕЖИМА "ИМИТАЦИЯ"\n')
    # checking_()

    print('ПРОВЕРКА РЕЖИМА "МАСКИРОВАНИЕ"\n')
    # checking_()


if __name__ == "__main__":
    main()