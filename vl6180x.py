import ustruct
import struct
import time
from machine import I2C

# i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=('P8', 'P9'))

class Sensor:
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self._address = address
        self.default_settings()
        self.init()

    def myWrite16(self, register, regValue):
        """ write a byte to specified 16 bit register """
        return self.i2c.writeto_mem(self._address, register, bytearray([regValue]), addrsize=16), 'big'

    def myRead16(self, register):
        """read 1 bit from 16 byte register"""
        # i2c.readfrom_mem(0x29, 0x0016, 1, addrsize=16)
        value = int.from_bytes(
            self.i2c.readfrom_mem(self._address, register, 1, addrsize=16),
            'big'
        )
        return value & 0xFFFF

    def init(self):
        if self.myRead16(0x0016) != 1:
            raise RuntimeError("Failure reset")

        # Recommended setup from the datasheet
     
        self.myWrite16(0x0207, 0x01)
        self.myWrite16(0x0208, 0x01)
        self.myWrite16(0x0096, 0x00)
        self.myWrite16(0x0097, 0xfd)
        self.myWrite16(0x00e3, 0x00)
        self.myWrite16(0x00e4, 0x04)
        self.myWrite16(0x00e5, 0x02)
        self.myWrite16(0x00e6, 0x01)
        self.myWrite16(0x00e7, 0x03)
        self.myWrite16(0x00f5, 0x02)
        self.myWrite16(0x00d9, 0x05)
        self.myWrite16(0x00db, 0xce)
        self.myWrite16(0x00dc, 0x03)
        self.myWrite16(0x00dd, 0xf8)
        self.myWrite16(0x009f, 0x00)
        self.myWrite16(0x00a3, 0x3c)
        self.myWrite16(0x00b7, 0x00)
        self.myWrite16(0x00bb, 0x3c)
        self.myWrite16(0x00b2, 0x09)
        self.myWrite16(0x00ca, 0x09)
        self.myWrite16(0x0198, 0x01)
        self.myWrite16(0x01b0, 0x17)
        self.myWrite16(0x01ad, 0x00)
        self.myWrite16(0x00ff, 0x05)
        self.myWrite16(0x0100, 0x05)
        self.myWrite16(0x0199, 0x05)
        self.myWrite16(0x01a6, 0x1b)
        self.myWrite16(0x01ac, 0x3e)
        self.myWrite16(0x01a7, 0x1f)
        self.myWrite16(0x0030, 0x00)

#  writeReg System__Fresh_OUT_OF_Reset
        # self.myWrite16(0x0016, 0x00),

    def default_settings(self):
        # Enables polling for ‘New Sample ready’ when measurement completes
        self.myWrite16(0x0011, 0x10)
        self.myWrite16(0x010A, 0x30)  # Set Avg sample period
        self.myWrite16(0x003f, 0x46)  # Set the ALS gain
        self.myWrite16(0x0031, 0xFF)  # Set auto calibration period
        # (Max = 255)/(OFF = 0)
        self.myWrite16(0x0040, 0x63)  # Set ALS integration time to 100ms
        # perform a single temperature calibration
        self.myWrite16(0x002E, 0x01)

        # Optional settings from datasheet
        self.myWrite16(0x001B, 0x09)  # Set default ranging inter-measurement
        # period to 100ms
        self.myWrite16(0x003E, 0x0A)  # Set default ALS inter-measurement
        # period to 100ms
        self.myWrite16(0x0014, 0x24)  # Configures interrupt on ‘New Sample
        # Ready threshold event’

        # Additional settings defaults from community
        self.myWrite16(0x001C, 0x32)  # Max convergence time
        self.myWrite16(0x002D, 0x10 | 0x01)  # Range check enables
        self.myWrite16(0x0022, 0x7B)  # Eraly coinvergence estimate
        self.myWrite16(0x0120, 0x01)  # Firmware result scaler

    def identify(self):
        """Retrieve identification information of the sensor."""
        return {
            'model': self.myRead16(0x0000),
            'revision': (self.myRead16(0x0001), self.myRead16(0x0002)),
            'module_revision': (self.myRead16(0x0003),
                                self.myRead16(0x0004)),
            'date': self.myRead16(0x006),
            'time': self.myRead16(0x008),
        }

    def address(self, address=None):
        """Change the I2C address of the sensor."""
        if address is None:
            return self._address
        if not 8 <= address <= 127:
            raise ValueError("Wrong address")
        self._set_reg8(0x0212, address)
        self._address = address

    def range(self):
        """Measure the distance in millimeters. Takes 0.01s."""
        self.myWrite16(0x0018, 0x01)  # Sysrange start
        time.sleep(0.01)
        return self.myRead16(0x0062)  # Result range valueimport ustruct
