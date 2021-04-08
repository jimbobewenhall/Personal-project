import Gyro_controller
import AC_D_converter
import GPIO_run
import traceback

class main:
    def __init__(self):
        self.controller = Gyro_controller()
        self.converter = AC_D_converter()
        self.GPIO = GPIO_run()

    def run(self):
        try:
            self.controller.get_values()
        except Exception:
            print(traceback.print_exc())
        try:
            self.converter.read()
        except Exception:
            print(traceback.print_exc())
        try:
            self.GPIO.run()
        except Exception:
            print(traceback.print_exc())