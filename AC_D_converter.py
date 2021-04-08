import smbus

class read_value:
    def __init__(self):
        self.address = 0x48
        self.bus = smbus.SMBus(1)

    def read(self):
        self.bus.write_byte(self.address,A0)
        self.value = self.bus.read_byte(self.address)
        print(self.value)
