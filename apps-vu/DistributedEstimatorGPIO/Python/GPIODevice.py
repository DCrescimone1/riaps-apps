# import riaps
# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import random
import os
import threading
import zmq
import time
import Adafruit_BBIO.GPIO as GPIO
# riaps:keep_import:end

class GPIODevice(Component):
# riaps:keep_constr:begin
    def __init__(self):
        super(GPIODevice, self).__init__()
        self.logger.info("GPIODevice - starting")
        ''' Enable GPIO '''
        self.pinName = 'USR2'
        self.initialValue = 0
        self.setupDelay = 60
        self.gpioOn = 1
        self.gpioOff = 0
        GPIO.setup(self.pinName,GPIO.OUT,GPIO.PUD_OFF,self.initialValue, self.setupDelay)
# riaps:keep_constr:end

# riaps:keep_blink:begin
    def on_blink(self):
        msg = self.blink.recv_pyobj()            # Receive blink message
        self.logger.info('on_blink():%s' % msg)
        ''' Toggle GPIO '''
        GPIO.output(self.pinName, self.gpioOn)
        time.sleep(0.250)
        GPIO.output(self.pinName, self.gpioOff)
# riaps:keep_blink:end

# riaps:keep_impl:begin
    def __destroy__(self):
        self.logger.info("GPIODevice - stopping")
        GPIO.output(self.pinName, self.gpioOff)
        time.sleep(0.250)
        GPIO.cleanup(self.pinName)
# riaps:keep_impl:end
