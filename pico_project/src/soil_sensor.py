import struct
import time
from machine import I2C


# 2 byte register address: 1st byte is module, 2nd byte is specific function
# status module/temp function, from adafruit seesaw standard
_STATUS_BASE = const(0x00)
_STATUS_TEMP = const(0x04)

# touch module/touch function, from adafruit seesaw standard
_TOUCH_BASE = const(0x0F)
_TOUCH_CHANNEL_OFFSET = const(0x10)

i2c = I2C(0, sda=0, scl=1)

class I2CDevice:
    def __init__(self, address):
        self.address = address
    
    def read(self, reg_base, reg, nbytes, delay=0.005):
        """Read an arbitrary I2C register range on the device"""
        self.write(reg_base, reg) # tell the device what we want to read
        time.sleep(delay)
        
        return bytearray(i2c.readfrom(self.address, nbytes))
    
    def write(self, reg_base, reg, buf=bytearray()):
        """Write an arbitrary I2C register range on the device"""
        register = bytearray([reg_base, reg])
        
        i2c.writeto(self.address, register + buf)


class SoilSensor(I2CDevice):
    def __init__(self):
        super().__init__(0x36)
    
    def moisture(self):
        """Read the value of the moisture sensor"""
        buf = self.read(_TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, 2)
        ret = struct.unpack(">H", buf)[0] # unpack big endian (>) unsigned shorts (H). there's only one so get the 0th index
        
        return ret
    
    def temp(self):
        """Read the temperature"""
        buf = self.read(_STATUS_BASE, _STATUS_TEMP, 4)
        buf[0] = buf[0] & 0b111111 # not sure why the first 2 bits are removed here. this byte is generally 0 anyway
        ret = struct.unpack(">I", buf)[0] # unpack big endian (>) unsigned ints (I). there's only one so get the 0th index
        return ret / 0x10000 # the value is multiplied by 0x10000 before being stored as an integer rather than using a float. undo that to get the original


if __name__ == '__main__':
    sensor = SoilSensor()
    from time import sleep

    for i in range(5):
        print(sensor.moisture())
        print(sensor.temp())
        sleep(1)