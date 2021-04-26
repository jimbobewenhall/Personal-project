import RPi.GPIO as GPIO

class run_GPIO:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # GPIO Numbers instead of board numbers
        self.south_GPIO = 16  # south
        self.west_GPIO = 26
        self.east_GPIO = 20
        self.north_GPIO = 12

    def south(self, on_off):
        GPIO.setup(self.south_GPIO, GPIO.OUT)
        if on_off is True:
            GPIO.output(self.south_GPIO, GPIO.LOW)  # out
        elif on_off is False:
            GPIO.output(self.south_GPIO, GPIO.HIGH)  # on

    def north(self, on_off):
        GPIO.setup(self.north_GPIO, GPIO.OUT)
        if on_off is True:
            GPIO.output(self.north_GPIO, GPIO.LOW)  # out
        elif on_off is False:
            GPIO.output(self.north_GPIO, GPIO.HIGH)  # on

    def east(self, on_off):
        GPIO.setup(self.east_GPIO, GPIO.OUT)
        if on_off is True:
            GPIO.output(self.east_GPIO, GPIO.LOW)  # out
        elif on_off is False:
            GPIO.output(self.east_GPIO, GPIO.HIGH)  # on

    def west(self, on_off):
        GPIO.setup(self.west_GPIO, GPIO.OUT)
        if on_off is True:
            GPIO.output(self.west_GPIO, GPIO.LOW)  # out
        elif on_off is False:
            GPIO.output(self.west_GPIO, GPIO.HIGH)  # on
