# from constants_FB_AP import CMDOP_REGISTER, CMDOP_MSG_OFF, STATUS1, PANELSIG
# from probably_not_used.TCP_Client import connect_client, close_client
# from read_and_write_functions import this_is_read_error, this_is_write_error
# from read_stutuses_and_message import read_status1_one_bit, read_panelsig_one_bit
# 
# 
# connect_client()
# 
# 
# def test_write_cmdop():
#     print('Проверка возможности записи команды управления (20)')
#     if this_is_write_error(address=CMDOP_REGISTER, value=CMDOP_MSG_OFF):
#         print('Ошибка записи команды управления 20(Включить/Отключить Генерацию сообщений) на ножку CmdOp.')
#     else:
#         print('Тест пройден - Запись команды управления 20(Включить/Отключить Генерацию сообщений) на ножку CmdOp.')
#     print()
# 
# 
# def test_enabling_and_disabling_message_generation_mode():
#     print('Проверка включения/отключения режима генерации сообщений.')
#     before_status1 = read_status1_one_bit(STATUS1['MsgOff'][0])
#     before_panelsig = read_panelsig_one_bit(PANELSIG['MsgOff'][0])
#     print(PANELSIG['MsgOff'][0], before_panelsig, STATUS1['MsgOff'][0], before_status1)
# 
#     # if 
# 
# 
# 
# test_write_cmdop()
# test_enabling_and_disabling_message_generation_mode()
# 
# close_client()
# 