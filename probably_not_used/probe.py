from TCP_Client import connect_client, close_client, client
from constants import CHECK_VALUE_WRITE_COILS, CHECK_VALUE_WRITE_COILS

connect_client()

print(
    f'client.read_coils(100, 10) - {client.read_coils(100, 10)}\n'
#     f'client.read_coils(100, 10).calculateRtuFrameSize - {client.read_coils(100, 10).calculateRtuFrameSize()}\n'
#     f'client.read_coils(100, 10).decode - {client.read_coils(100, 10).decode()}\n'
#     f'client.read_coils(100, 10) - {client.read_coils(100, 10).doException()}\n'
    f'client.read_coils(100, 10)encode() - {client.read_coils(100, 10).encode()}\n'
    f'client.read_coils(100, 10).function_code - {client.read_coils(100, 10).function_code}\n'
    f'client.read_coils(100, 10).get_response_pdu_size() - {client.read_coils(100, 10).get_response_pdu_size()}\n'
    f'client.read_coils(100, 10).isError() - {client.read_coils(100, 10).isError()}\n'
#     f'client.read_coils(100, 10).setData() - {client.read_coils(100, 10).setData()}\n'
    f'client.read_coils(100, 10).sub_function_code - {client.read_coils(100, 10).sub_function_code}\n'
    f'client.read_coils(100, 10).sub_function_code - {client.read_coils(100, 10)}\n'
    f'client.write_coils(100, CHECK_VALUE_WRITE_COILS) - {client.write_coils(100, CHECK_VALUE_WRITE_COILS)}\n'
    f'client.read_holding_registers(100, 10, slave=1).registers - {client.read_holding_registers(100, 10, slave=1).registers}\n'
    f'client.read_discrete_inputs(100, 10) - {client.read_discrete_inputs(100, 10).bits}\n'
    f'client.read_input_registers(100, 10, slave=1).registers - {client.read_input_registers(100, 10, slave=1).registers}\n'
    f'client.read_holding_registers(100, 10, slave=1).registers - {client.read_holding_registers(200, 1, slave=1).registers}\n'
)
while True:
    print(f'{client.read_holding_registers(200, 75, slave=1).registers}')
client.read_holding_registers(100, 10, slave=1).registers
close_client()