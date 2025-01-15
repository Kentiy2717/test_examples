from probably_not_used.constants import SLAVE
from common_wrappers import checking_the_value_for_writing, sleep_time_after_operation

from encode_and_decode import decode_int, encode_float, encode_int, decode_float
from probably_not_used.TCP_Client import client


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
def read_coils(address, count=1, bit=None, slave=1):
    if bit is not None:
        return client.read_coils(address=address, count=count, slave=slave).bits[bit]
    else:
        return client.read_coils(address=address, count=count, slave=slave)


@sleep_time_after_operation
def write_holding_register(address, value, slave=1):
    '''В CmdOp писать через нее!'''
    return client.write_register(address=address, value=value, slave=slave)


@checking_the_value_for_writing
@sleep_time_after_operation
def write_holding_registers(address, values, slave=1, skip_error=False):
    return client.write_registers(address=address, values=encode_float(values), slave=slave)


@checking_the_value_for_writing
@sleep_time_after_operation
def write_holding_registers_int(address, values, slave=1, skip_error=False):
    return client.write_registers(address=address, values=encode_int(values), slave=slave)


def read_holding_registers(address, count=1, slave=1):
    return client.read_holding_registers(address=address, count=count, slave=slave)


def read_discrete_inputs(address, count=1, bit=None, slave=1):
    if bit is not None:
        return client.read_discrete_inputs(address=address, count=count, slave=slave).bits[bit]
    else:
        return client.read_discrete_inputs(address=address, count=count, slave=slave)


def read_float(address: int):
    return decode_float(read_holding_registers(address=address, count=2))


def read_int(address: int):
    return decode_int(read_holding_registers(address=address, count=1))
