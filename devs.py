import serial
import time
import logging

def read_reg(dev_addr:int, reg_addr:int, reg_num:int, ser_path:str = '/dev/ttyUSB0'):
    """
    Read Reg function (function 3 of modbus).
    读取寄存器函数, (modbus功能3).

    dev_addr: device address [int] 0 ~ 255
    reg_addr: reg address [int] 0~2^16
    reg_num: number of reg [int] 0~2^16
    ser_path: '/dev/ttyUSB0' [str]
    """
    assert (dev_addr < 256) and (dev_addr >= 0)
    with serial.Serial(ser_path, 9600, timeout=1) as ser:
        # send the function 3 request
        # Format: AA 03 RRRR NNNN CCCC
        # AA: address 0-255
        # 03: function 3
        # RRRR: Reg address
        # NNNN: Reg num
        # CCCC: CRC correct
        dev_addr_bytes = dev_addr.to_bytes(1, byteorder='big')
        reg_addr_bytes = reg_addr.to_bytes(2, byteorder='big')
        reg_num_bytes = reg_num.to_bytes(2, byteorder='big')
        cmd = dev_addr_bytes + b'\x03' + reg_addr_bytes + reg_num_bytes
        crc_code = crc16(cmd)
        # logging.debug(f'Send cmd {cmd+crc_code}')
        print("Send CMD: ", end='')
        print_bytes(cmd+crc_code)
        ser.write(cmd+crc_code)
        r = ser.read(1000)
        print("Read RESPON: ", end='')
        print_bytes(r)
        if crc16(r[:-2]) == r[-2:]:
            return r[3:-2]
        return False


def set_reg(dev_addr:int, reg_addr:int, reg_status:bool, ser_path:str = '/dev/ttyUSB1'):
    """
    Set Reg function (function 5 of modbus).
    设置单个寄存器函数, (modbus功能5).

    dev_addr: device address [int] 0 ~ 255
    reg_addr: reg address [int] 0~2^16
    reg_status: true on / false off [bool] 
    ser_path: '/dev/ttyUSB0' [str]
    """
    assert (dev_addr < 256) and (dev_addr >= 0)
    with serial.Serial(ser_path, 9600, timeout=1) as ser:
        # send the function 3 request
        # Format: AA 05 RRRR VVVV CCCC
        # AA: address 0-255
        # 05: function 5
        # RRRR: Reg address
        # VVVV: Reg value  [on]:FF00H/[off]:0000H
        # CCCC: CRC correct
        dev_addr_bytes = dev_addr.to_bytes(1, byteorder='big')
        reg_addr_bytes = reg_addr.to_bytes(2, byteorder='big')
        reg_value_bytes = b'\xFF\x00' if reg_status else b'\x00\x00'
        cmd = dev_addr_bytes + b'\x05' + reg_addr_bytes + reg_value_bytes
        crc_code = crc16(cmd)
        print_bytes(cmd+crc_code)
        ser.write(cmd+crc_code)
        r = ser.read(1000)
        print_bytes(r)
        if r == cmd+crc_code:
            return True
        return False


def crc16(data: bytes):
    crc_table = [0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241, 0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440, 0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40, 0x0A00, 0xCAC1, 0xCB81, 0x0B40,
                 0xC901, 0x09C0, 0x0880, 0xC841, 0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40, 0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41, 0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
                 0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040, 0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240, 0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441, 0x3C00, 0xFCC1, 0xFD81, 0x3D40,
                 0xFF01, 0x3FC0, 0x3E80, 0xFE41, 0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840, 0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41, 0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
                 0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640, 0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041, 0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240, 0x6600, 0xA6C1, 0xA781, 0x6740,
                 0xA501, 0x65C0, 0x6480, 0xA441, 0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41, 0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840, 0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
                 0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40, 0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640, 0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041, 0x5000, 0x90C1, 0x9181, 0x5140,
                 0x9301, 0x53C0, 0x5280, 0x9241, 0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440, 0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40, 0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
                 0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40, 0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41, 0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641, 0x8201, 0x42C0, 0x4380, 0x8341,
                 0x4100, 0x81C1, 0x8081, 0x4040]

    crc_hi = 0xFF
    crc_lo = 0xFF

    for w in data:
        index = int(crc_lo) ^ w
        crc_val = crc_table[int(index)]
        crc_temp = crc_val >> 8
        crc_val_low = crc_val - (crc_temp << 8)
        crc_lo = crc_val_low ^ crc_hi
        crc_hi = crc_temp

    return bytes([crc_lo, crc_hi])


def print_bytes(p_bytes):
    print(''.join(['\\x%02x' % b for b in p_bytes])) 


def parse_potcol(p_bytes: bytes, potcol_type: str='TEMP'):
    """
    Parse the potocol

    :param p_bytes: bytes
    :param potcol_type: str
    """
    assert potcol_type in ['TEMP', 'VWC', 'EC', 'SALINITY', 'TDS', 'EPSILON']
    # Temperature potcol
    if potcol_type == 'TEMP':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        if a > 8000:
            a = a - 0xFFFF - 1
        print('Temperature: ', a/100.0, 'C')
        return a/100.0
    if potcol_type == 'VWC':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        print('Volumn Water Content: ', a/100.0, '%')
        return a/100.0
    if potcol_type == 'EC':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        print('EC: ', a/100.0, 'us/cm')
        return a/100.0
    if potcol_type == 'SALINITY':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        print('Salinity: ', a, 'mg/L')
        return a
    if potcol_type == 'TDS':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        print('TDS: ', a, 'mg/L')
        return a
    if potcol_type == 'EPSILON':
        assert(len(p_bytes) == 2)
        a = int.from_bytes(p_bytes, byteorder='big', signed=False)
        print('Epsilon: ', a/100.0, )
        return a/100.0


def pump_once(pump_time: int=2):
    """
    进行一次浇花任务， 一次浇花任务包括：
    1. 打开水泵
    2. 等待一段时间
    3. 关闭水泵
    """
    r = set_reg(dev_addr=255, reg_addr=1, reg_status=True, ser_path='/dev/ttyUSB1')
    time.sleep(pump_time)
    r = set_reg(dev_addr=255, reg_addr=1, reg_status=False, ser_path='/dev/ttyUSB1')


def read_status() -> dict:
    address_type = {0: 'TEMP', 1:'VWC', 2:'EC', 3: 'SALINITY', 4: 'TDS', 5: 'EPSILON'}
    status = {}
    for address, value_type in address_type.items():
        r = read_reg(dev_addr=4, reg_addr=address, reg_num=1, ser_path='/dev/ttyUSB0')
        status[value_type] = parse_potcol(r, value_type)
    return status

if __name__ == '__main__':
    read_status()
    
