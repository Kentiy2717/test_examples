'''
Тестирование ФБ АП (Функциональный блок аналогового параметра).

Список тестов:
1. Проверка пересчета измеренного значения (test_recalculated_measured_value).
2. Проверка нормального значения (test_normal_value).
'''
from assist_function import check_status, setup_limit_value, working_with_limit_value
from constants_FB_AP import (
    STATUS_FOR_CHECK_STATUS,
    VALUES_FOR_LOW_LEVEL,
    VALUES_FOR_MID_LEVEL,
    MAX_NORMATIVE_VALUE_LOW_LEVEL,
    MAX_NORMATIVE_VALUE_MID_LEVEL,
    NORMAL_VALUE_MID_LEVEL,
    NORMAL_VALUE_LOW_LEVEL,
    INPUT,
    OUT,
)
from probably_not_used.TCP_Client import connect_client, close_client, client


connect_client()


def test_recalculated_measured_value():
    '''
    Проверка пересчета измеренного значения(test_recalculated_measured_value).

    Описание:
        В цикле передаем последовательно индекс, который соответствует порядковому номеру элементов в списках
        значений аналогового параметра для нижнего и среднего уровня(VALUES_FOR_LOW_LEVEL, VALUES_FOR_MID_LEVEL).
        Далее считываем пересчитанное значений со среднего уровня (read_values_for_mid_level).
        и сравнение с эталонным значением из списка (VALUES_FOR_MID_LEVEL[index]).
        Если списки совпадают, то тест считается пройденным.

    Параметры:
        VALUES_FOR_LOW_LEVEL: список значений, которые подаются для записи на нижний уровень.
        VALUES_FOR_MID_LEVEL: список эталонных значений, которые должны получиться после пересчета.
        read_values_for_mid_level: список значений, которые получаются после пересчета.
        INPUT: номер регистра для чтения и записи аналогового параметра (нижний уровень).
        OUT: номер регистра для чтения и записи аналогового параметра (средний уровень).

    Принцип работы:
        1. Подаем значения на запись на нижний уровень в цикле.
        2. Читаем и сохраняем пересчитанное значения со среднего уровня в переменную read_values_for_mid_level.
        3. Сравниваем полученное значение с эталонным (VALUES_FOR_MID_LEVEL[index]).
        4. Цикл продолжает свою работу, пока не пройдет по всем элементам списка(VALUES_FOR_LOW_LEVEL).
    '''

    for index in range(0, len(VALUES_FOR_LOW_LEVEL)):
        client.write_registers(address=INPUT, values=VALUES_FOR_LOW_LEVEL[index], slave=1)
        read_values_for_mid_level = client.read_holding_registers(
            address=OUT, count=2, slave=1
        ).registers
        assert read_values_for_mid_level == VALUES_FOR_MID_LEVEL[index], (
            'Полученные значения не совпадают с эталонными.'
        )


# setup_limit_value()  # Установка предельных значений аналогового параметра


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
        NORMAL_VALUE_LOW_LEVEL: значение для записи на нижний уровень.
        NORMAL_VALUE_MID_LEVEL: эталонноеначальное значение (средний уровень).
        read_normal_value_mid_level: значение аналогового параметра после пересчета(средний уровень).
        STATUS_FOR_CHECK_STATUS: Словарь для проверки статусов аналогового параметра, начиная с обрыва и заканчивая КЗ.
        INPUT: номер регистра для чтения и записи аналогового параметра (нижний уровень).
        OUT: номер регистра для чтения и записи аналогового параметра (средний уровень).


    Принцип работы:
        1. Подаем значение равное (NORMAL_VALUE_LOW_LEVEL) на запись на нижний уровень.
        2. Считываем и записываем пересчитанное значение в переменную(read_normal_value_mid_level)
        2. Сравниваем полученное значение(read_normal_value_mid_level) с эталонным значением(NORMAL_VALUE_MID_LEVEL).
        3. Читаем статусы(check_status) аналогового параметра и сравниваем с эталонным значением из словаря
        STATUS_FOR_CHECK_STATUS по ключу ['Нормальное значение'].
    '''

    client.write_register(address=INPUT, value=NORMAL_VALUE_LOW_LEVEL, slave=1)
    read_normal_value_mid_level = client.read_holding_registers(
        address=OUT, count=1, slave=1
    ).registers[0]
    assert read_normal_value_mid_level == NORMAL_VALUE_MID_LEVEL, 'Значение параметра не совпадает с эталонным.'
    assert check_status() == STATUS_FOR_CHECK_STATUS['Нормальное значение'], (
        'Статусы аналогового параметра не совпадают с эталонными.'
    )


def test_maximum_normative_value():
    '''
    Проверка максимального нормативного значения (test_maximum_normative_value).

    Описание:
        Вызывается вспомогательная функция (working_with_limit_value), в которую передается 4 аргумента.
        Функция возвращает список со списками статусов в различных состояниях. 
        Подробнее о работе функции working_with_limit_value в описании к этой фунции.
        Значения данного списка сравниваются с эталонными значениями (эталонные значения
        получены из словаря STATUS_FOR_CHECK_STATUS по ключу 'Максимальное нормативное значение'.
        При совпадении значений, тест считается пройденным.

    Параметры:
        limit_value_low_level: уставка максимального нормативного значения(нижний уровень).
        limit_value_mid_level: уставка максимального нормативного значения(верхний уровень).
        num_registr_low_level: регистр для записи максимального нормативного значения(нижний уровень).
        num_registr_mid_level: регистр для записи  максимального нормативного значения(верхний уровень).

    Принцип работы:
        1. Вызывается функция working_with_limit_value, в которую передается 4 аргумента.
        Данные, возвращенные функцией, сравниваются с эталонными значениями статусов из словаря
        STATUS_FOR_CHECK_STATUS по ключу 'Максимальное нормативное значение'.
    '''

    assert working_with_limit_value(
        limit_value_low_level=MAX_NORMATIVE_VALUE_LOW_LEVEL,
        limit_value_mid_level=MAX_NORMATIVE_VALUE_MID_LEVEL,
        num_registr_low_level=None,
        num_registr_mid_level=None) == STATUS_FOR_CHECK_STATUS['Максимальное нормативное значение']


def test_maximum_limit_value():
    '''Проверка максимального предельного значения.'''


def test_maximum_emergency_value():
    '''Проверка максимального аварийного значения.'''


def test_upper_limit_of_measurement():
    '''Проверка верхнего предела измерения(Короткое замыкание).'''


def test_minimum_normative_value():
    '''Проверка минимального нормативного значения.'''


def test_minimum_limit_value():
    '''Проверка минимального предельного значения.'''


def test_minimum_emergency_value():
    '''Проверка минимального аварийного значения.'''


def test_lower_limit_of_measurement():
    '''Проверка нижнего предела измерения(Обрыв).'''


def test_work_mode():
    '''
    Проверка режима "Полевая обработка"(test_work_mode).

    Описание:
        Вызывается вспомогательная функция (working_with_limit_value), в которую передается 4 аргумента.
        Функция возвращает список со списками статусов в различных состояниях. 
        Подробнее о работе функции working_with_limit_value в описании к этой фунции.
        Значения данного списка сравниваются с эталонными значениями (эталонные значения
        получены из словаря STATUS_FOR_CHECK_STATUS по ключу 'Максимальное нормативное значение'.
        При совпадении значений, тест считается пройденным.

    Параметры:
        limit_value_low_level: уставка максимального нормативного значения(нижний уровень).
        limit_value_mid_level: уставка максимального нормативного значения(верхний уровень).
        num_registr_low_level: регистр для записи максимального нормативного значения(нижний уровень).
        num_registr_mid_level: регистр для записи  максимального нормативного значения(верхний уровень).

    Принцип работы:
        1. Вызывается функция working_with_limit_value, в которую передается 4 аргумента.
        Данные, возвращенные функцией, сравниваются с эталонными значениями статусов из словаря
        STATUS_FOR_CHECK_STATUS по ключу 'Максимальное нормативное значение'.
    '''










def test_simulation_mode():
    '''Проверка режима "Имитация".'''


def test_test_mode():
    '''Проверка режима "Тестирование".'''


def test_mask_mode():
    '''Проверка режима "Маскирования".'''


close_client()
