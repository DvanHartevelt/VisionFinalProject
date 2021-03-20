# This is the final project for the Vision course
# At Saxion in Enschede


# by David van Hartevelt, March 2021

import cv2
import numpy as np
import time
import SeperatorClass


def getMask(mask, minArea=1000):
    """
    Finds the largest mask of a coloured egg, and returns said mask.

    :param mask: mask after HSV ranging
    :param minArea: Minimum area of egg
    :return: isEgg: Bool if there is an egg at all
             newMask: new mask
    """
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    finalContours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.015 * peri, True)
            finalContours.append([area, approx, contour])

    finalContours = sorted(finalContours, key=lambda x:x[0], reverse=True)

    if len(finalContours) == 0: return False, mask

    h, w = np.array(mask).shape
    maskNew = np.zeros((h, w), np.uint8)
    maskNew = cv2.fillPoly(maskNew, [finalContours[0][1]], 255)

    im_floodfill = maskNew.copy()

    h, w = maskNew.shape[:2]
    maskk = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(im_floodfill, maskk, (0, 0), 255);
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    newnewMask = maskNew|im_floodfill_inv

    return True, newnewMask

def getEggColour(img):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # h_min, h_max, s_min, s_max, v_min, v_max = printTrackbars(printing=False)
    lower = np.array([0, 29, 113])
    upper = np.array([179, 255, 255])
    mask = cv2.inRange(imgHSV, lower, upper)
    isEgg, maskNew = getMask(mask)

    # result = cv2.bitwise_and(eggs[index], eggs[index], mask=maskNew)

    if isEgg:
        mean = cv2.mean(imgHSV, maskNew)

        colourNames = ["red", "yellow", "green", "blue"]
        colourHues = [18, 25, 82, 94]

        closestColourIndex = 0
        for i in range(len(colourHues)):
            if abs(colourHues[i] - mean[0]) < abs(colourHues[closestColourIndex] - mean[0]):
                closestColourIndex = i

        # print(f"The colour of this egg is: {colourNames[closestColourIndex]}, with an area of {cv2.countNonZero(maskNew)}.")
        return colourNames[closestColourIndex]
    else:
        # print("No egg in field of view")
        return "None"



def main():
    imgBlue = cv2.imread("Testpictures/BlueEgg.jpeg")
    imgRed = cv2.imread("Testpictures/RedEgg.jpeg")
    imgWhite = cv2.imread("Testpictures/WhiteEgg.jpeg")
    imgGreen = cv2.imread("Testpictures/GreenEgg.jpeg")
    imgNoEgg = cv2.imread("Testpictures/NoEgg.jpeg")

    eggs = [imgRed, imgNoEgg, imgGreen, imgNoEgg, imgWhite, imgNoEgg, imgBlue, imgNoEgg]

    starttime = time.time()
    index = 0

    lastSeenColour = "None"

    divide = SeperatorClass.Seperator()

    # def printTrackbars(printing=True):
    #     h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
    #     h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
    #     s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
    #     s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
    #     v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
    #     v_max = cv2.getTrackbarPos("Val Max", "Trackbars")
    #
    #     if printing: print(h_min, h_max, s_min, s_max, v_min, v_max)
    #
    #     return h_min, h_max, s_min, s_max, v_min, v_max
    #
    # cv2.namedWindow("Trackbars")
    # cv2.resizeWindow("Trackbars", 640, 240)
    # cv2.createTrackbar("Hue Min", "Trackbars", 0, 255, printTrackbars)
    # cv2.createTrackbar("Hue Max", "Trackbars", 179, 255, printTrackbars)
    # cv2.createTrackbar("Sat Min", "Trackbars", 29, 255, printTrackbars)
    # cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, printTrackbars)
    # cv2.createTrackbar("Val Min", "Trackbars", 113, 255, printTrackbars)
    # cv2.createTrackbar("Val Max", "Trackbars", 255, 255, printTrackbars)

    while True:
        seenColour = getEggColour(eggs[index])

        if seenColour != "None" and seenColour != lastSeenColour:
            lastSeenColour = seenColour
            if lastSeenColour == "red":
                divide.open()
            else:
                divide.close()

        print(f"Last seen colour egg: {lastSeenColour}.")

        divide.do()

        cv2.imshow("Egg", eggs[index])
        cv2.waitKey(1)

        if time.time() - starttime > 2:
            starttime = time.time()
            index = (index + 1) % len(eggs)



if __name__ == "__main__":
    main()
