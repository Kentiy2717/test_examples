from time import sleep
from common_read_and_write_functions import read_holding_registers
from constants_FB_AP import MESSAGES_START_REGISTER, MESSAGES_STOP_REGISTER
from probably_not_used.constants import SLEEP_TIME_FOR_READ_MESSAGE


def read_all_messages():
    sleep(SLEEP_TIME_FOR_READ_MESSAGE)
    all_messages = []
    for message in range(MESSAGES_START_REGISTER, MESSAGES_STOP_REGISTER, 2):
        all_messages.append(read_holding_registers(address=message, count=2).registers)
    return all_messages


def read_new_messages(old_messages):
    '''Возвращает отсортированный список с новыми сообщениями'''
    now_messages = read_all_messages()
    new_messages = []
    for i in range(0, 50):
        if now_messages[i] != old_messages[i]:
            new_messages.append(now_messages[i][0])
    new_messages.sort()
    return new_messages
