import RPi.GPIO as GPIO
import time
import numpy as np


GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo = GPIO.PWM(11,50)

servo.start(0)

class Seperator:
    def __init__(self):
        self.duty = 2.0
        self.rotation = 80

    def open(self):
        self.rotation = 20
        self.duty = np.interp(self.rotation, [0, 180], [2, 12])
        print(self.duty)
        servo.ChangeDutyCycle(self.duty)
        pass

    def close(self):
        self.rotation = 80
        self.duty = np.interp(self.rotation, [0, 180], [2, 12])
        print(self.duty)
        servo.ChangeDutyCycle(self.duty)
        pass