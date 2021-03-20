import RPi.GPIO as GPIO
import time
import numpy as np


# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(11, GPIO.OUT)
# servo = GPIO.PWM
#
# servo.start(0)

class Seperator:
    def __init__(self):
        self.duty = 2.0
        self.rotation = 0

    def open(self):
        self.rotation = 60
        pass

    def close(self):
        self.rotation = 0
        pass

    def do(self):
        self.duty = np.interp(self.rotation, [0, 180], [2, 12])
        print(self.duty)
        # servo.ChangeDutyCycle(self.duty)