from probably_not_used.constants import SLAVE
from wrappers_FB_AP import sleep_time_after_operation

from encode_and_decode import encode_float, encode_int, decode_float
from probably_not_used.TCP_Client import client
from constants_FB_AP import (
    CMDOP,
    REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST as LEGS,
)


@sleep_time_after_operation
def this_is_write_error(address, value, slave=SLAVE):
    if type(value) is int:
        return client.write_registers(address=address, values=encode_int(value), slave=slave).isError()
    elif type(value) is float:
        return client.write_registers(address=address, values=encode_float(value), slave=slave).isError()    
    elif type(value) is bool:
        return client.write_coil(address=address, value=value, slave=slave).isError()
    


def this_is_read_error(address, count, slave=SLAVE):
    return client.read_holding_registers(address=address, count=count, slave=slave).isError()


@sleep_time_after_operation
def write_coil(address, value, slave=1):
    return client.write_coil(address=address, value=value, slave=slave)


@sleep_time_after_operation
def read_coils(address, count=1, slave=1):
    return client.read_coils(address=address, count=count, slave=slave)


@sleep_time_after_operation
def write_holding_register(address, value, slave=1):
    '''В CmdOp писать через нее!'''
    return client.write_register(address=address, value=value, slave=slave)


@sleep_time_after_operation
def write_holding_registers(address, values, slave=1):
    return client.write_registers(address=address, values=encode_float(values), slave=slave)


def read_holding_registers(address, count, slave=1):
    return client.read_holding_registers(address=address, count=count, slave=slave)


def read_discrete_inputs(address, count=1, bit=None, slave=1):
    if bit is not None:
        return client.read_discrete_inputs(address=address, count=count, slave=slave).bits[bit]
    else:
        return client.read_discrete_inputs(address=address, count=count, slave=slave)


def read_float(address: int):
    return decode_float(read_holding_registers(address=address, count=2))


@sleep_time_after_operation
def reset_CmdOp():
    '''Обнуляет CmdOp.'''

    write_holding_register(address=LEGS['CmdOp']['register'], value=0)


@sleep_time_after_operation
def write_CmdOp(command=0):
    '''Обнуляет CmdOp, а потом записывает значение переданнов в value.'''

    reset_CmdOp()
    if type(command) is str:
        write_holding_register(address=LEGS['CmdOp']['register'], value=CMDOP[command])
    else:
        write_holding_register(address=LEGS['CmdOp']['register'], value=command)
