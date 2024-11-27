from TCP_Client import connect_client, close_client, client
from probably_not_used.color_print import print_error
from constants import (
    CHECK_VALUE_WRITE_COILS,
    CHECK_VALUE_WRITE_REGISTERS,
    VALUE_INPUT_REGISTERS,
    VALUE_HOLDING_REGISTERS
    )

# Установка соединения с сервером
connect_client()


def test_cannot_write_inactive_register():
    assert client.write_coil(
        110, True, slave=1
        ).isError() is True
    assert client.write_coils(
        110, CHECK_VALUE_WRITE_COILS, slave=1
        ).isError() is True
    assert client.write_register(
        110, 55, slave=1
    ).isError() is True
    assert client.write_registers(
        110, CHECK_VALUE_WRITE_REGISTERS, slave=1
        ).isError() is True


def test_cannot_read_inactive_register():
    assert client.read_coils(
        110, 8, slave=1
        ).isError() is True
    assert client.read_discrete_inputs(
        110, 8, slave=1
        ).isError() is True
    assert client.read_input_registers(
        110, 8, slave=1
        ).isError() is True
    assert client.read_holding_registers(
        110, 8, slave=1
        ).isError() is True


def test_write_one_coil():
    assert client.write_coil(
        109, 1, slave=1
        ).isError() is False


def test_write_many_coils():
    assert client.write_coils(
        100, CHECK_VALUE_WRITE_COILS, slave=1
        ).isError() is False


def test_read_coils():
    assert client.read_coils(
        100, 10, slave=1
        ).bits[:10] == CHECK_VALUE_WRITE_COILS


def test_write_one_holding_register():
    assert client.write_register(109, 999).isError() is False


def test_write_many_holding_registers():
    assert client.write_registers(
        100, CHECK_VALUE_WRITE_REGISTERS, slave=1
    ).isError() is False


def test_read_registers():
    assert client.read_holding_registers(
        100, len(CHECK_VALUE_WRITE_REGISTERS), slave=1
    ).registers == CHECK_VALUE_WRITE_REGISTERS


def test_read_discrete_inputs():
    assert client.read_discrete_inputs(
        100, len(VALUE_INPUT_REGISTERS), slave=1
        ).bits[:len(VALUE_INPUT_REGISTERS)] == VALUE_INPUT_REGISTERS


def test_read_input_registers():
    '''Тестирование корректного считывания AI регистров.'''
    read_value = client.read_input_registers(
        address=100,
        count=len(VALUE_HOLDING_REGISTERS),
        slave=1
        ).registers[:len(VALUE_HOLDING_REGISTERS)]
    message = (f'Ошибка в чтении данных.\n\n'
               f'Ожидаемое значение:    {VALUE_HOLDING_REGISTERS}\n'
               f'Полученное значение:   {read_value}\n')
    assert read_value == VALUE_HOLDING_REGISTERS, message


read_value = client.read_input_registers(
    address=100,
    count=len(VALUE_HOLDING_REGISTERS),
    slave=1
    ).registers[:len(VALUE_HOLDING_REGISTERS)]
if read_value != VALUE_HOLDING_REGISTERS:
    print_error(
        'Ошибка в чтении данных (test_read_input_registers).\n',
        f'Ожидаемое значение:   {VALUE_HOLDING_REGISTERS}',
        f'Полученное значение:  {read_value}')

close_client()
