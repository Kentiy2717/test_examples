from constants_FB_AP import CMDOP_REGISTER, CMDOP_MSG_OFF
from TCP_Client import client

def this_is_write_error(address, value):
    return client.write_register(address=address, value=value).isError()

def this_is_read_error():
    pass

def read_holding_registers():
    pass