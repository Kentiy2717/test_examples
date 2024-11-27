'''
Тестирование ФБ АП (Функциональный блок аналогового параметра).

Список тестов:
1. Проверка пересчета измеренного значения (test_recalculated_measured_value).
2. Проверка нормального значения (test_normal_value).
'''
from assist_function import check_status
from constants_FB_AP import (
    HYSTERESIS,
    STATUS_FOR_CHECK_STATUS,
    START_VALUE_LOW_LEVEL,
    START_VALUE_MID_LEVEL,
    VALUES_FOR_LOW_LEVEL,
    VALUES_FOR_MID_LEVEL)
from TCP_Client import connect_client, close_client, client


connect_client()


def test_recalculated_measured_value():
    '''
    Проверка пересчета измеренного значения(test_recalculated_measured_value).

    Описание:
        Подается список значений на нижний уровень (VALUES_FOR_LOW_LEVEL).
        После чего происходит чтение пересчитанных значений со среднего уровня (read_values_for_mid_level).
        и сравнение с эталонным списком значений (VALUES_FOR_MID_LEVEL).
        Если списки совпадают, то тест считается пройденным.

    Параметры:
        VALUES_FOR_LOW_LEVEL: список значений, которые подаются на нижний уровень.
        VALUES_FOR_MID_LEVEL: список эталонных значений, которые должны получиться после пересчета.'
        read_values_for_mid_level: список значений, которые получаются после пересчета.

    Принцип работы:
        1. Подаем значения на запись на нижний уровень.
        2. Читаем пересчитанные значения со среднего уровня в список read_values_for_mid_level.
        3. Сравниваем полученные значения с эталонным списком VALUES_FOR_MID_LEVEL.
    '''

    client.write_registers(100, VALUES_FOR_LOW_LEVEL, slave=1)
    read_values_for_mid_level = client.read_holding_registers(100, len(VALUES_FOR_MID_LEVEL), slave=1).registers
    assert read_values_for_mid_level == VALUES_FOR_MID_LEVEL, 'Полученные значения не совпадают с эталонными.'


def test_normal_value():
    '''
    Проверка нормального значения (test_normal_value).

    Описание:
        Подается значение на запись на нижний уровень (NORMAL_VALUE_LOW_LEVEL).
        После чего происходит чтение пересчитанных значений со среднего уровня (read_start_value_mid_level)
        и сравнение с эталонным значением (NORMAL_VALUE_MID_LEVEL). Если значения совпадают, то
        вызывается функция check_status() которая возвращает список со статусами аналогового параметра.
        Список сравнивается с эталонным, который содержится в словаре STATUS_FOR_CHECK_STATUS
        под ключом 'Нормальное значение'. Если списки совпадают, то тест считается пройденным.

    Параметры:
        HYSTERESIS: гистерезис.
        START_VALUE_LOW_LEVEL: значение для записи на нижний уровень.
        START_VALUE_MID_LEVEL: эталонноеначальное значение (средний уровень).

    Принцип работы:
        1. Подаем значение равное (START_VALUE_LOW_LEVEL) на запись на нижний уровень.
        2. Сравниваем полученное значение на среднем уровне с эталонным значением.
        3. Читаем статусы аналогового параметра и сравниваем с эталонным.
    '''

    client.write_register(100, NORMAL_VALUE_LOW_LEVEL[0], slave=1)
    read_start_value_mid_level = client.read_holding_registers(100, 1, slave=1).registers
    assert read_start_value_mid_level == NORMAL_VALUE_MID_LEVEL, 'Значение параметра не совпадает с эталонным.'
    assert check_status(client=client) == STATUS_FOR_CHECK_STATUS['Нормальное значение'], (
        'Статусы аналогового параметра не совпадают с эталонными.'
    )


def test_maximum_normative_value():
    '''
    Проверка максимального нормативного значения (test_maximum_normative_value).

    Описание:
        Подается значение на запись на нижний уровень (MAX_NORMATIVE_VALUE_LOW_LEVEL).
        После чего происходит чтение пересчитанных значений со среднего уровня (read_start_value_mid_level)
        и сравнение с эталонным значением (MAX_NORMATIVE_VALUE_MID_LEVEL). Если значения совпадают, то
        вызывается функция check_status() которая возвращает список со статусами аналогового параметра.
        Список сравнивается с эталонным, который содержится в словаре STATUS_FOR_CHECK_STATUS
        под ключом 'Максимальное нормативное значение'. Если списки совпадают, то тест считается пройденным.

    Параметры:
        MAX_NORMATIVE_VALUE_LOW_LEVEL: уставка максимального нормативного значения.

    Принцип работы:
        1. Подаем значение равное (START_VALUE_LOW_LEVEL) на запись на нижний уровень.
        2. Сравниваем полученное значение на среднем уровне с эталонным значением.
        2. Сравниваем полученное значение с эталонным значением на .
        3. Подаем значение равное (START_VALUE - HYSTERESIS/2) на запись на нижний уровень.
        4. Читаем статусы аналогового параметра и сравниваем с эталонным.
        5. Подаем значение равное (START_VALUE) на запись на нижний уровень.
        4. Читаем статусы аналогового параметра и сравниваем с эталонным.
        5. Подаем значение равное (START_VALUE + 2 * HYSTERESIS) на запись на нижний уровень.
        6. Читаем статусы аналогового параметра и сравниваем с эталонным.
        7. Подаем значение равное (START_VALUE) на запись на нижний уровень.
        8. Читаем статусы аналогового параметра и сравниваем с эталонным.
        9. Подаем значение равное (START_VALUE - HYSTERESIS/2) на запись на нижний уровень.
        10. Читаем статусы аналогового параметра и сравниваем с эталонным.
        11. Подаем значение равное (START_VALUE - 2 * HYSTERESIS) на запись на нижний уровень.
    '''
    check_status(client)


def test_maximum_limit_value():
    '''Проверка максимального предельного значения.'''


def test_maximum_emergency_value():
    '''Проверка максимального аварийного значения.'''


def test_upper_limit_of_measurement():
    '''Проверка верхнего предела измерения(Короткое замыкание).'''


def test_return_to_normal_value():
    '''
    Проверка смены статусов при возвращении значения в норму(test_return_to_normal_value).
    '''


def test_minimum_normative_value():
    '''Проверка минимального нормативного значения.'''


def test_minimum_limit_value():
    '''Проверка минимального предельного значения.'''


def test_minimum_emergency_value():
    '''Проверка минимального аварийного значения.'''


def test_lower_limit_of_measurement():
    '''Проверка нижнего предела измерения(Обрыв).'''








def test_simulation_mode():
    '''Проверка режима "Имитация".'''


def test_work_mode():
    '''Проверка режима "Полевая обработка".'''


def test_test_mode():
    '''Проверка режима "Тестирование".'''


def test_mask_mode():
    '''Проверка режима "Маскирования".'''


close_client()
