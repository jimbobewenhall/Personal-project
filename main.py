from IR_read import Infrared_remote
#from Gyro_read import controller
from GPIO_run import run_GPIO
from ADS_read import ADS
from math import isclose
import time
import threading
from multiprocessing import Queue, Process
import concurrent.futures
import statistics
import smbus

GPIO_controller = run_GPIO()

ADS_reader = ADS()
infrared = Infrared_remote()
class controller:
    def __init__(self):
        self.PWR_MGMT_1 = 0x6B
        self.SMPLRT_DIV = 0x19
        self.CONFIG = 0x1A
        self.GYRO_CONFIG = 0x1B
        self.INT_ENABLE = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H = 0x43
        self.GYRO_YOUT_H = 0x45
        self.GYRO_ZOUT_H = 0x47

        self.MPU_Init()


    def MPU_Init(self):
        self.bus = smbus.SMBus(3)  # or bus = smbus.SMBus(0) for older version boards
        self.Device_Address = 0x68  # MPU6050 device address

        # write to sample rate register
        self.bus.write_byte_data(self.Device_Address, self.SMPLRT_DIV, 7)

        # Write to power management register
        self.bus.write_byte_data(self.Device_Address, self.PWR_MGMT_1, 1)

        # Write to Configuration register
        self.bus.write_byte_data(self.Device_Address, self.CONFIG, 0)

        # Write to Gyro configuration register
        self.bus.write_byte_data(self.Device_Address, self.GYRO_CONFIG, 24)

        # Write to interrupt enable register
        self.bus.write_byte_data(self.Device_Address, self.INT_ENABLE, 1)


    def read_raw_data(self, addr):
        # Accelero and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.Device_Address, addr)
        low = self.bus.read_byte_data(self.Device_Address, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if (value > 32768):
            value = value - 65536
        return value



    def get_values(self):
        # Read Accelerometer raw value
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)

        # Read Gyroscope raw value
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

        # Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0

        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        return Ax, Ay
  
control = controller()  
def run_main():
    override = False
    direction = ''

######################################################################
############### Edit these values to change accuracy #################
######################################################################

    margin = 0.02       ### Accuracy of solar panel movement,
                        ###    lower is better. ###
    voltage = 0.9       ### The wind voltage required to go flat. ###
    move_time = 5       ### In manual mode the seconds the actuator
                        ###    is activated on each button press. ### 
    dark_value = 1.5    ### The voltage of the solar panel for it
                        ###    to go to night mode. ###
    gyro_margin = 0.05  ### The accuracy of the go flat script. ###
    wind_sleep = 5000   ### Time in seconds the script stops after
                        ###    going flat in the wind loop. ###
    night_sleep = 600   ### Time in seconds the script stops after
                        ###    doing the night loop. ###

######################################################################
######################################################################
######################################################################


    while True:
        try:
            time.sleep(1)
            start_time = time.time()
            Key = infrared.read()
            print(Key)
            value_list = ADS_reader.read_values()  # [0]=north [1]=east [2]=south [3]=west [4]=wind
            print('North/South: '+str(round(value_list[0], 3))+' - '+str(round(value_list[2], 3)))
            print('East/West: '+str(round(value_list[1], 3))+' - '+str(round(value_list[3], 3)))
            print('Wind speed: '+str(round(value_list[4], 3)))
            print('Movement direction: '+str(direction))

            if str(Key) =='KEY_STOP':
                override = 'stop'
                
            elif str(Key) == 'KEY_EXIT':
                override = True

            elif Key == 'KEY_PLAY':
                override = False

            if override is False and value_list[4] < voltage and value_list[0] > dark_value:
                print('Normal loop')
                if isclose(value_list[0], value_list[2], abs_tol=margin) is False:
                    x = max(value_list[0], value_list[2])
                    if x != value_list[0]:
                        GPIO_controller.north(True)
                        GPIO_controller.south(False)
                        direction = 'North'
                    else:
                        GPIO_controller.south(True)
                        GPIO_controller.north(False)
                        direction = 'South'
                        
                else:
                    GPIO_controller.south(False)
                    GPIO_controller.north(False)
                    direction = ''

                if isclose(value_list[1], value_list[3], abs_tol=margin) is False:
                    x = max(value_list[1], value_list[3])
                    if x == value_list[1]:
                        GPIO_controller.east(True)
                        GPIO_controller.west(False)
                        direction = direction+'East'
                    else:
                        GPIO_controller.west(True)
                        GPIO_controller.east(False)
                        direction = direction+'West'
                else:
                    direction = direction+''
                    GPIO_controller.west(False)
                    GPIO_controller.east(False)

            elif value_list[4] > voltage and override is False and value_list[0] > dark_value:
                print('Wind loop')
                while value_list[4] > voltage:
                    value_list = ADS_reader.read_values()
                    aX, aY = control.get_values()
                    time.sleep(1)

                    if isclose(0, aX, abs_tol=gyro_margin) is False:
                        while aX < 0.01:
                            aX, aY = control.get_values()
                            time.sleep(1)
                            GPIO_controller.south(True)
                            GPIO_controller.north(False)
                        GPIO_controller.south(False)

                        while aX > -0.01:
                            aX, aY = control.get_values()
                            time.sleep(1)
                            GPIO_controller.north(True)
                            GPIO_controller.south(False)
                        GPIO_controller.north(False)

                    if isclose(0, aY, abs_tol=gyro_margin) is False:
                        while aY > 0.01:
                            aX, aY = control.get_values()
                            time.sleep(1)
                            GPIO_controller.east(True)
                            GPIO_controller.west(False)
                        GPIO_controller.east(False)

                        while aY < -0.01:
                            aX, aY = control.get_values()
                            time.sleep(1)
                            GPIO_controller.west(True)
                            GPIO_controller.east(False)
                        GPIO_controller.west(False)
                    time.sleep(wind_sleep)
                
            elif str(Key) == 'KEY_EXIT':
                print('Flat override loop')
                aX, aY = control.get_values()
                time.sleep(1)

                if isclose(0, aX, abs_tol=gyro_margin) is False:
                    while aX < 0.01:
                        aX, aY = control.get_values()
                        print(aX)
                        GPIO_controller.south(True)
                        GPIO_controller.north(False)
                        time.sleep(1)
                    GPIO_controller.south(False)

                    while aX > -0.01:
                        aX, aY = control.get_values()
                        print(aX)
                        GPIO_controller.north(True)
                        GPIO_controller.south(False)
                        time.sleep(1)
                    GPIO_controller.north(False)

                if isclose(0, aY, abs_tol=gyro_margin) is False:
                    while aY > 0.01:
                        aX, aY = control.get_values()
                        print(aY)
                        GPIO_controller.east(True)
                        GPIO_controller.west(False)
                        time.sleep(1)
                    GPIO_controller.east(False)

                    while aY < -0.01:
                        aX, aY = control.get_values()
                        print(aY)
                        GPIO_controller.west(True)
                        GPIO_controller.east(False)
                        time.sleep(1)
                    GPIO_controller.west(False)
                
            elif value_list[0] < dark_value and override is False:
                print('Night loop')
                aX, aY = control.get_values()
                time.sleep(1)

                if isclose(0, aX, abs_tol=gyro_margin) is False:
                    while aX < 0.01:
                        aX, aY = control.get_values()
                        time.sleep(1)
                        GPIO_controller.south(True)
                        GPIO_controller.north(False)
                    GPIO_controller.south(False)

                    while aX > -0.01:
                        aX, aY = control.get_values()
                        time.sleep(1)
                        GPIO_controller.north(True)
                        GPIO_controller.south(False)
                    GPIO_controller.north(False)

                if isclose(0, aY, abs_tol=gyro_margin) is False:
                    while aY > 0.01:
                        print(aY)
                        aX, aY = control.get_values()
                        time.sleep(1)
                        GPIO_controller.east(True)
                        GPIO_controller.west(False)
                    GPIO_controller.east(False)

                    while aY < -0.01:
                        aX, aY = control.get_values()
                        time.sleep(1)
                        GPIO_controller.west(True)
                        GPIO_controller.east(False)
                    GPIO_controller.west(False)
                time.sleep(night_sleep)

            elif override == 'stop': # in override mode
                GPIO_controller.north(False)
                GPIO_controller.south(False)
                GPIO_controller.east(False)
                GPIO_controller.west(False)
                if str(Key) == 'KEY_UP':
                    GPIO_controller.north(True)
                    GPIO_controller.south(False)
                    time.sleep(move_time)
                    GPIO_controller.north(False)
                elif str(Key) == 'KEY_OK':
                    GPIO_controller.south(True)
                    GPIO_controller.north(False)
                    time.sleep(move_time)
                    GPIO_controller.south(False)
                elif str(Key) == 'KEY_LEFT':
                    GPIO_controller.east(True)
                    GPIO_controller.west(False)
                    time.sleep(move_time)
                    GPIO_controller.east(False)
                elif str(Key) == 'KEY_RIGHT':
                    GPIO_controller.west(True)
                    GPIO_controller.east(False)
                    time.sleep(move_time)
                    GPIO_controller.west(False)

            end_time = time.time()-start_time
            print('Loop time: '+str(int(end_time))+' seconds')
        except:
            print('error')
            time.sleep(10)
            pass

if __name__ == '__main__':
    run_main()

    
