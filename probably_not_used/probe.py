import sys
import os

# Эта строка добавляет путь к корневой директории проекта в sys.path, чтобы Python мог находить модули и пакеты,
# расположенные в этом проекте, независимо от текущей директории запуска скрипта.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.common_read_and_write_functions import (
    read_coils,
    read_discrete_inputs,
    this_is_write_error,
    write_coil,
    write_holding_register,
    write_holding_registers,
    read_holding_registers,
    read_float,
    write_holding_registers_int
)
from probably_not_used.TCP_Client import close_client, connect_client


connect_client()

# write_coil(address=40122, value=1, slave=1)
# write_coil(address=40121, value=1, slave=1)
# write_coil(address=40136, value=1, slave=1)
# write_coil(address=40137, value=1, slave=1)
write_holding_register(address=11800, value=9)
# write_coil(address=40137, value=0, slave=1)
print(read_coils(address=40136).bits)
print(read_coils(address=40137).bits)
# write_holding_registers(address=40126, values=0, slave=1)
# write_holding_registers(address=40127, values=0, slave=1)


close_client()
