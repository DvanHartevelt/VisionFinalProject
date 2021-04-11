# This is the final project for the Vision course
# At Saxion in Enschede


# by David van Hartevelt, March 2021

import cv2
import numpy as np
import time
#import SeperatorClass
from ImageFunctions import getEggColour, warpImg
import RPi.GPIO as GPIO

def main():
    Testpictures = False
    useServo = True
    samplingfrequency = 4 # in Hz

    dtmax = 1 / samplingfrequency

    if useServo:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(13, GPIO.OUT)
        servo = GPIO.PWM(13, 50)
        servo.start(6.4) # 6.4 is open, 6.1 is closed

    if Testpictures:
        imgBlue = cv2.imread("Testpictures/BlueEgg.jpeg")
        imgRed  = cv2.imread("Testpictures/RedEgg.jpeg")
        imgWhite = cv2.imread("Testpictures/WhiteEgg.jpeg")
        imgGreen = cv2.imread("Testpictures/GreenEgg.jpeg")
        imgNoEgg = cv2.imread("Testpictures/NoEgg.jpeg")

        eggs = [imgRed, imgNoEgg, imgGreen, imgNoEgg, imgWhite, imgNoEgg, imgBlue, imgNoEgg]

        starttime = time.time()
        index = 0
    else:
        cap = cv2.VideoCapture(0)
        pass

    lastSeenColour = "None"

    t0 = time.time()
    while True:
        t1 = time.time()
        dt = t1 - t0

        if dt > dtmax: # this is so the detection is only done 4 times per second
            # Step 1: retrieving the picture, and extracting the colour
            if Testpictures:
                seenColour, hue = getEggColour(eggs[index])
            else:
                ret, frame = cap.read()

                windowPoints = [[300, 300], [300, 200], [400, 300], [400, 200]]
                window = warpImg(frame, windowPoints, 300, 300)

                cv2.imshow("Camera capture", frame)
                cv2.imshow("window", window)
                cv2.waitKey(1)

                seenColour, hue = getEggColour(window, useSliders=True)
                # print(f"Seen colour: {seenColour}")

            # Step 2: Checking if the bottom path needs to be closed
            if seenColour != "None" and seenColour != lastSeenColour:
                lastSeenColour = seenColour
                print(f"Hue found was {hue}.")
                if lastSeenColour == "red":
                    print("Closing bottom path")
                    if useServo:
                        servo.ChangeDutyCycle(3.1)
                else:
                    print("Opening bottom path")
                    if useServo:
                        servo.ChangeDutyCycle(6.4)


            if Testpictures:
                cv2.imshow("Egg", eggs[index])
                cv2.waitKey(1)
                if time.time() - starttime > 2:
                    starttime = time.time()
                    index = (index + 1) % len(eggs)

def testCam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        print(ret)

        cv2.imshow("Camera capture", frame)
        cv2.waitKey(100)




if __name__ == "__main__":
    #testCam()
    main()
