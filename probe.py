from time import sleep

from TCP_Client import connect_client, close_client, client
from assist_function import encode_float, encode_int, decode_float, decode_bits, decode_uint

connect_client()

# print(client.write_coil(address=40101, value=False))
# print(client.write_coil(address=40102, value=False))
# print(client.write_coil(address=40103, value=False))
# print(client.write_coil(address=40104, value=False))
# print(client.write_coil(address=40105, value=False))
# print(client.write_coil(address=40106, value=False))
# print(client.write_coil(address=40107, value=False))
# print(client.write_coil(address=40108, value=False))
# print(client.write_coil(address=40109, value=False))
# print(client.write_coil(address=40110, value=False))
# print(client.write_register(address=801, value=20))
# client.write_coil(address=40100, value=0)
# print(client.read_coils(address=40100, count=1).bits)
# while True:
#     print(client.write_register(address=801, value=2))
#     sleep(2)
#     print(client.write_register(address=801, value=4))
#     sleep(2)
# client.write_coil(address=40103, value=0)

# payload = encode_float(-256.525)
# while True:
#     for value in range(3, 22, 1):
#         payload = encode_float(value)
#         print(payload)
#         print(client.write_registers(address=40500, values=payload, skip_encode=True))
#         sleep(2)
#     for value in range(22, 3, -1):
#         payload = encode_float(value)
#         print(payload)
#         print(client.write_registers(address=40500, values=payload, skip_encode=True))
#         sleep(2)
# 
# print(client.read_holding_registers(address=0, count=2).registers)
# result  = client.read_holding_registers(address=0, count=2)
# result_decode = decode_float(result)
# print(type(result_decode))
# print(result_decode)
print(client.write_register(address=801, value=27))
sleep(1)
print(client.write_register(address=801, value=4))
sleep(1)
# print(client.write_register(address=801, value=20).isError())
# sleep(1)
print(client.read_holding_registers(address=0, count=2).registers)
sleep(1)
result = client.read_holding_registers(address=0, count=2)
print(result.registers)
print(decode_uint(result))
print(decode_bits(result))
print(3 - 2 // 8)
print(7 - 2 % 8)
result = client.read_holding_registers(address=21677, count=1)
print(result.registers)
print(encode_int(result))
print(decode_bits(result))



# print(client.read_holding_registers(address=1201, count=2).registers)
# result  = client.read_holding_registers(address=1201, count=2)
# decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.BIG, wordorder=Endian.LITTLE)
# print ("read_holding_registers Out: " + str(decoder.decode_32bit_float()))
# 
# print(client.read_holding_registers(address=1203, count=1).registers)
# result  = client.read_holding_registers(address=1203, count=1)
# decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.BIG, wordorder=Endian.LITTLE)

# print(client.read_holding_registers(address=2001, count=2).registers)
# print(client.read_holding_registers(address=40501, count=2).registers)
# print(client.read_holding_registers(address=40503, count=2).registers)
# print(client.read_holding_registers(address=40505, count=2).registers)
# 
# 
# print(client.read_holding_registers(address=40101, count=2).registers)
# print(client.read_holding_registers(address=40102, count=2).registers)
# print(client.read_holding_registers(address=40103, count=2).registers)
# print(client.read_holding_registers(address=40104, count=2).registers)
# print(client.read_holding_registers(address=40105, count=2).registers)
close_client()