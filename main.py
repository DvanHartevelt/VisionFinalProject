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
    Testpictures = True
    useServo = False

    if useServo:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT)
        servo = GPIO.PWM(11, 50)
        servo.start(6.4) # 6.4 is open, 6.1 is closed

    if Testpictures:
        imgBlue = cv2.imread("Testpictures/BlueEgg.jpeg")
        imgRed = cv2.imread("Testpictures/RedEgg.jpeg")
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

    while True:
        if Testpictures:
            seenColour = getEggColour(eggs[index])
        else:
            ret, frame = cap.read()

            windowPoints = [[300, 300], [300, 200], [400, 300], [400, 200]]
            window = warpImg(frame, windowPoints, 300, 300)

            cv2.imshow("Camera capture", frame)
            cv2.imshow("window", window)
            cv2.waitKey(1)

            seenColour = getEggColour(window)
            # print(f"Seen colour: {seenColour}")

        if seenColour != "None" and seenColour != lastSeenColour:
            lastSeenColour = seenColour
            if lastSeenColour == "red":
                print("opening")
                if useServo:
                    servo.ChangeDutyCycle(3.1)
                # divide.open()
            else:
                print("closing")
                if useServo:
                    servo.ChangeDutyCycle(6.4)
                #divide.close()

        #print(f"Last seen colour egg: {lastSeenColour}.")

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
