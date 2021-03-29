# This is the final project for the Vision course
# At Saxion in Enschede


# by David van Hartevelt, March 2021

import cv2
import numpy as np
import time
import SeperatorClass
from ImageFunctions import getEggColour

def main():
    testing = True

    if testing:
        imgBlue = cv2.imread("Testpictures/BlueEgg.jpeg")
        imgRed = cv2.imread("Testpictures/RedEgg.jpeg")
        imgWhite = cv2.imread("Testpictures/WhiteEgg.jpeg")
        imgGreen = cv2.imread("Testpictures/GreenEgg.jpeg")
        imgNoEgg = cv2.imread("Testpictures/NoEgg.jpeg")

        eggs = [imgRed, imgNoEgg, imgGreen, imgNoEgg, imgWhite, imgNoEgg, imgBlue, imgNoEgg]

        starttime = time.time()
        index = 0
    else:
        # TODO implement camera interaction

        # cap = cv2.VideoCapture(0)
        pass

    lastSeenColour = "None"

    divide = SeperatorClass.Seperator()

    while True:
        if testing:
            seenColour = getEggColour(eggs[index])
        else:
            pass

        if seenColour != "None" and seenColour != lastSeenColour:
            lastSeenColour = seenColour
            if lastSeenColour == "red":
                divide.open()
            else:
                divide.close()

        print(f"Last seen colour egg: {lastSeenColour}.")

        if testing:
            cv2.imshow("Egg", eggs[index])
            cv2.waitKey(1)

            if time.time() - starttime > 2:
                starttime = time.time()
                index = (index + 1) % len(eggs)

def testCam():
    cap = cv2.VideoCapture(0)

    i = 0

    while True:

        if i % 100 == 0:

            ret, frame = cap.read()
            print(ret)

            cv2.imshow("Camera capture", frame)


        i += 1




if __name__ == "__main__":
    testCam()
    main()
