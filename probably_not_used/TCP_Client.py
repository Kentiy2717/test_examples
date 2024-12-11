import sys

from pymodbus.client import ModbusTcpClient

from probably_not_used.constants import HOST, PORT
from func_print_console_and_write_file import print_text_grey, print_error, write_to_file


client = ModbusTcpClient(host=HOST, port=PORT)


def connect_client():
    write_to_file('______________________________________________________')
    print_text_grey('\n\nПодключение клиента...')
    try:
        if not client.connect():
            raise Exception
    except Exception:
        print_error(f'Соединение с серверном не установлено. {Exception}\n'
                    f'Проверьте работоспособность сервера и '
                    f'параметры подключения в файле constants.py\n\n'
                    f'Дальнейшая работа невозможна. Останавливаю работу программы.\n')
        sys.exit()
    print_text_grey('Подключение установлено\n\n')


def close_client():
    print_text_grey('\nОстановка клиента...')
    client.close()
    print_text_grey('Стоп\n\n')
