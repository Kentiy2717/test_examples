from constants import HYSTERESIS, REGISTERS_FOR_CHECK_STATUS


def check_status(client):
    '''
    Чтение статуса аналогового параметра со всех регистров.

    Параметры:
        REGISTERS_FOR_CHECK_STATUS: список регистров для проверки статуса аналогового параметра.

    Принцип работы:
        1. Создаем пустой список для записи статусов аналогового параметра.
        2. Проходимся циклом по списку регистров.
        3. Считываем статус и записываем в список.
        4. Возвращаем список статусов аналогового параметра.

    '''
    list_status = []
    for register in REGISTERS_FOR_CHECK_STATUS:
        status = client.read_holding_registers(register, 1).registers[0]  # ???
        list_status.append(status)
    return list_status


def working_with_setpoints(client, setpoint):
    '''
    Функция для работы с уставками.

    Функция принимает три аргумента:
        1. client - клиент Modbus TCP.
        2. setpoint - уставка аналогового параметра.
    
    Описание:

            
    '''