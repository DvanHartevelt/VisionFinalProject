# This is the final project for the Vision course
# At Saxion in Enschede


# by David van Hartevelt, March 2021

import cv2
import time
from ImageFunctions import getEggColour, warpImg
import RPi.GPIO as GPIO

def main():
    # Debug variables
    Testpictures = False
    useServo = True
    samplingfrequency = 24 # in Hz
    saveRedpic = False
    saveBluepic = False
    saveYellowpic = True

    # 'global' variables in this function
    dtmax = 1 / samplingfrequency
    takepic = 0
    pictexEggcolor = 'None'

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
            # resetting timing
            t0 = t1

            # Step 1: retrieving the picture
            if Testpictures:
                window = eggs[index]
            else:
                ret, frame = cap.read()

                windowPoints = [[300, 300], [300, 200], [400, 300], [400, 200]]
                window = warpImg(frame, windowPoints, 300, 300)

                cv2.imshow("Camera capture", frame)
                cv2.imshow("window", window)
                cv2.waitKey(1)

                if takepic > 0:
                    cv2.imwrite(f"Output/{pictexEggcolor}CameraCapture{takepic}.png", frame)
                    cv2.imwrite(f"Output/{pictexEggcolor}Window{takepic}.png", window)

            # Step 2: extracting egg colour
            seenColour, hue = getEggColour(window, useSliders=True, takepic=takepic, pictexEggcolor=pictexEggcolor)

            # Step 3: Checking if the bottom path needs to be closed
            if seenColour != "None" and seenColour != lastSeenColour:
                lastSeenColour = seenColour
                print(f"New hue found was {hue}. This is the colour {seenColour}.")
                if lastSeenColour == "red":
                    if saveRedpic:
                        takepic = 5
                        pictexEggcolor = "red"
                        saveRedpic = False

                    print("Closing bottom path")
                    if useServo:
                        servo.ChangeDutyCycle(3.1)
                else:
                    if saveBluepic and lastSeenColour == "blue":
                        takepic = 5
                        pictexEggcolor = "blue"
                        saveBluepic = False

                    if saveYellowpic and lastSeenColour == "yellow":
                        takepic = 5
                        pictexEggcolor = "yellow"
                        saveBluepic = False
                    print("Opening bottom path")
                    if useServo:
                        servo.ChangeDutyCycle(8.0)

            # Debug, showing the picture taken from the pre-loaded set.
            if Testpictures:
                cv2.imshow("Egg", eggs[index])
                cv2.waitKey(1)
                if time.time() - starttime > 2:
                    starttime = time.time()
                    index = (index + 1) % len(eggs)

            if takepic != 0: takepic -= 1

if __name__ == "__main__":
    main()
