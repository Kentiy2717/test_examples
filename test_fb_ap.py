from TCP_Client import connect_client, close_client, client


connect_client()

def test_recalculated_measured_value():
    '''Проверка пересчета измеренного значения.'''
    assert False



def test_upper_limit_of_measurement():
    '''Проверка верхнего предела измерения(Короткое замыкание).'''
    assert 1 == True


def test_lower_limit_of_measurement():
    '''Проверка нижнего предела измерения(Обрыв).'''
    assert 1 == True


def test_minimum_emergency_value():
    '''Проверка минимального аварийного значения.'''


def test_maximum_emergency_value():
    '''Проверка максимального аварийного значения.'''

def test_minimum_limit_value():
    '''Проверка минимального предельного значения.'''

def test_maximum_limit_value():
    '''Проверка максимального предельного значения.'''

def test_minimum_regulatory_value():
    '''Проверка минимального нормативного значения.'''

def test_maximum_regulatory_value():
    '''Проверка максимального нормативного значения.'''


def test_simulation_mode():
    '''Проверка режима "Имитация".'''


def test_work_mode():
    '''Проверка режима "Полевая обработка".'''


def test_test_mode():
    '''Проверка режима "Тестирование".'''


def test_mask_mode():
    '''Проверка режима "Маскирования".'''

close_client()