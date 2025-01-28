import sys
import os

# Эта строка добавляет путь к корневой директории проекта в sys.path, чтобы Python мог находить модули и пакеты,
# расположенные в этом проекте, независимо от текущей директории запуска скрипта.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itertools import combinations
from time import sleep

from common.constants import DETAIL_REPORT_ON
from common.common_wrappers import (
    running_time,
    connect_and_close_client,
    writes_func_failed_or_passed
)
from common.func_print_console_and_write_file import (
    print_passed,
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
    write_holding_registers,
    write_holding_registers_int
)
from common.read_messages import read_all_messages, read_new_messages
from FB_VLV.assist_function_FB_VLV import (
    switch_position,
    turn_on_mode
)
from FB_VLV.constants_FB_VLV import (
    BAD_REGISTER,
    CMDOP,
    CMDOP_REGISTER,
    OUT_REGISTER,
    PANELMODE,
    PANELSIG,
    PANELSTATE,
    START_VALUE,
    STATUS1,
    STATUS2,
    SWITCH,
    WORK_MODES
)
from FB_VLV.read_and_write_functions_FB_VLV import write_CmdOp
from FB_VLV.read_stutuses_and_message_FB_VLV import (
    read_PanelAlm_one_bit,
    read_PanelMode,
    read_PanelSig_one_bit,
    read_PanelState,
    read_status1_one_bit,
    read_status2_one_bit
)
from FB_VLV.wrappers_FB_VLV import reset_initial_values


@reset_initial_values
@writes_func_failed_or_passed
# Проверка ошибок при записи c нулевым и положительными значениями(отрицательные не предусмотрены).
def checking_errors_writing_registers(not_error):
    print_title('Проверка ошибок при записи c нулевым и положительными значениями'
                '(отрицательные не предусмотрены).')

    # Создаем словарь с регистрами и значениями.
    data = {
        'Tls':         (99, 0),
        'Tmp':         (99, 0),
        'Terr':        (99, 0),
        'Tpulse':      (99, 0),
        'CmdOp':       (99, 0),
        'Delta':       (99.9, 0.0),
        'SetPos':      (99.9, 0.0),
        'AutSet':      (99.9, 0.0),
        'InPos':       (99.9, 0.0),
        'RLControl':   (True, False),
        'RLKey':       (True, False),
        'LocalClose':  (True, False),
        'LocalOpen':   (True, False),
        'LocalStop':   (True, False),
        'AutClose':    (True, False),
        'AutOpen':     (True, False),
        'FbkClose':    (True, False),
        'FbkOpen':     (True, False),
        'FbkClosing':  (True, False),
        'FbkOpening':  (True, False),
        'FbkMoving':   (True, False),
        'Fault':       (True, False),
        'ModDI_FLT':   (True, False),
        'ModDO_FLT':   (True, False),
        'CCOpen':      (True, False),
        'CCClose':     (True, False),
        'CCStop':      (True, False),
        'ExtFlt':      (True, False),
        'VolCtrl':     (True, False),
        'Permission':  (True, False),
        'InterlockO':  (True, False),
        'InterlockC':  (True, False),
        'Protect':     (True, False),
        'SafeOn':      (True, False),
        'SafePos':     (True, False),
        'PosFbk':      (True, False),
        'OffUnState':  (True, False),
        'Fbking':      (True, False),
    }
    # Проходимся циклом по всем регистрам и значениям для записии. Создаем переменные для проверки.
    for name, values in data.items():
        register = START_VALUE[name]['register']
        for value in values:
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
    print_error('ОШИБКА ПО ПРИЧИНЕ ТОГО, ЧТО БАГ. СООБЩЕНИЯ НЕ ДОЛЖНЫ ФОРМИРОВАТЬСЯ.')

    # Убеждаемся, что генерация сообщений включена.
    switch_position(command='MsgOff', required_bool_value=False)
    # Читаем сообщения. Переключаемся в режим "Авто".
    old_messages = read_all_messages()
    not_error = turn_on_mode(mode='Auto', not_error=not_error)

    # Получаем значение MsgOff и Auto в статус1.
    MsgOff = read_status1_one_bit(STATUS1['MsgOff'])
    Auto = read_status1_one_bit(STATUS1['Auto'])

    # Если режим "Авто" включен и сообщения сформировались, то выводим сообщение и проверяем дальше.
    if Auto is True and read_new_messages(old_messages) != []:
        print_text_grey(f'Сообщение о переходе в режим "Авто" сформировано. При MsgOff={MsgOff}')

        # Отключаем генерацию сообщений. Читаем сообщения.
        switch_position(command='MsgOff', required_bool_value=True)
        old_messages = read_all_messages()

        # Устанавливаем  режим "Дистанционный". Получаем значение Man из статус1.
        not_error = turn_on_mode(mode='Man', not_error=not_error)
        MsgOff = read_status1_one_bit(STATUS1['MsgOff'])
        Man = read_status1_one_bit(STATUS1['Man'])

        # Если уставка сработала и сообщение не формируется, то проверка пройдена.
        if Man is True and read_new_messages(old_messages) == []:
            print_text_grey(f'Сообщение о переходе в режим "Дистанционный" не сформировано. При MsgOff={MsgOff}')
        else:
            print_error(
                f'Сообщение о переходе в режим "Дистанционный" сформировалось при MsgOn={MsgOff}. '
                f'Дальнейшие тесты нецелесообразны (Man={Man}).'
            )
            not_error = False
    else:
        print_error(
            f'Сообщение о переходе в режим "Авто" не сформировалось при MsgOn={MsgOff}. '
            f'Дальнейшие тесты нецелесообразны (Auto={Auto}).'
        )
        not_error = False
    return not_error


@reset_initial_values
@writes_func_failed_or_passed
# Проверка правильности переложения SetPos, AutSet и INPos в Out, VUSetPos b VUPos в режимах "Дистанция" и "Авто",
# а также при включении режима имитация.
def checking_(not_error):
    print_title('Проверка правильности переложения SetPos, AutSet и INPos в '
                'Out, VUSetPos и VUPos в режимах "Дистанция" и "Авто", а также при включении режима имитация.')

    # Проверяем в цикле сначала режим "Дистанция", затем "Авто"
    for mode in ('Man', 'Auto'):
        pass
    
    return not_error


test_functions = {
    'Проверка ошибок при записи c нулевым и положительными значениями(отрицательные не предусмотрены).': checking_errors_writing_registers,
    'Проверка работы переключателей (командой на CmdOp).': cheking_on_off_for_cmdop,
    'Проверка включения и отключения режима генерации сообщений (командой на CmdOp).': checking_generation_messages_and_msg_off,
    'checking_': checking_,
}


@running_time
# @start_with_limits_values
@connect_and_close_client
def main(selected_functions=None, lock=None):
    '''
    Главная функция для запуска тестов ФБ VLV.
    '''
    print_text_white('СТАРТ ТЕСТИРОВАНИЯ ФБ VLV\n')

    if selected_functions is None:
        for func in test_functions.values():
            func()
    else:
        for description in selected_functions:
            test_functions[description]()

    print_passed('ТЕСТИРОВАНИЕ ФБ VLV ОКОНЧЕНО\n')


if __name__ == "__main__":
    main(test_functions)
