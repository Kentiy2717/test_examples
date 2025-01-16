from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder


def encode_float(float_value):  # Рабочая
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    builder.add_32bit_float(float_value)
    payload = builder.build()
    return payload


def decode_float(result_read_registers):  # Рабочая
    decoder = BinaryPayloadDecoder.fromRegisters(result_read_registers.registers, Endian.BIG, wordorder=Endian.LITTLE)
    return decoder.decode_32bit_float()


def encode_int(int):  # Рабочая
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    builder.add_16bit_int(int)
    payload = builder.build()
    return payload


def decode_int(result_read_registers):  # Рабочая
    decoder = BinaryPayloadDecoder.fromRegisters(result_read_registers.registers, Endian.BIG, wordorder=Endian.LITTLE)
    return decoder.decode_16bit_int()


def decoder_bits(result_read_registers):  # Рабочая
    list_bits = []
    package_len = [3, 4, 1, 2]
    for len in package_len:
        decoder = BinaryPayloadDecoder.fromRegisters(
            result_read_registers.registers,
            byteorder=Endian.BIG,
            wordorder=Endian.LITTLE
        )
        list_bits.append((decoder.decode_bits(package_len=len))[::-1])
    return list_bits
