import sys

from pymodbus.client import ModbusTcpClient

from constants import HOST, PORT


client = ModbusTcpClient(host=HOST, port=PORT)


def connect_client():
    print('Подключение клиента...')
    try:
        if not client.connect():
            raise Exception
    except Exception:
        print(f'Соединение с серверном не установлено. {Exception}\n'
              f'Проверьте работоспособность сервера и '
              f'параметры подключения в файле constants.py\n\n'
              f'Дальнейшая работа невозможна. Останавливаю работу программы.')
        sys.exit()
    print('Подключение установлено\n')


def close_client():
    print('Остановка клиента...')
    client.close()
    print('Стоп')