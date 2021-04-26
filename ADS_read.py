import time
import ADS1263
import RPi.GPIO as GPIO


class ADS:
    def __init__(self):
        self.REF = 5.08          # Modify according to actual voltage
                            # external AVDD and AVSS(Default), or internal 2.5
        self.ADC = ADS1263.ADS1263()
        if (self.ADC.ADS1263_init() == -1):
            exit()

    def read_values(self):
        #self.ADC.ADS1263_DAC_Test(1, 1)      # Open IN6
        #self.ADC.ADS1263_DAC_Test(0, 1)      # Open IN7

        ADC_Value = self.ADC.ADS1263_GetAll()    # get ADC1 value
        value_list = []
        for i in range(0, 10):
            if(ADC_Value[i]>>31 ==1):
                value_list.append(self.REF*2 - ADC_Value[i] * self.REF / 0x80000000)
            else:
                value_list.append(ADC_Value[i] * self.REF / 0x7fffffff) # 32bit

        return value_list

   

