import cv2
import numpy as np

def getMask(mask, minArea=1000):
    """
    Finds the largest mask of a coloured egg, and returns said mask.

    :param mask: mask after HSV ranging
    :param minArea: Minimum area of egg
    :return: isEgg: Bool if there is an egg at all
             newMask: new mask
    """
    # Finding all contours in image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # filtering the contours by minimum area size
    finalContours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.015 * peri, True)
            finalContours.append([area, approx, contour])

    # sorting the contours by area size, so the biggest one
    # (presumably the egg) is the first element
    finalContours = sorted(finalContours, key=lambda x: x[0], reverse=True)

    if len(finalContours) == 0:
        # No egg in the picture
        return False, mask
    else:
        # making a new mask out of the contour approximation
        h, w = mask.shape[:2]
        maskNew = np.zeros((h, w), np.uint8)
        maskNew = cv2.fillPoly(maskNew, [finalContours[0][2]], 255)

        # Filling in the new contour-based mask
        im_floodfill = maskNew.copy()
        maskk = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(im_floodfill, maskk, (0, 0), 255);
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)
        newnewMask = maskNew | im_floodfill_inv

        return True, newnewMask

def getEggColour(img, useSliders = False):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    if not useSliders:
        lower = np.array([0, 58, 113])
        upper = np.array([179, 255, 255])
    else:
        h_min, h_max, s_min, s_max, v_min, v_max = printTrackbars(printing=False)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(imgHSV, lower, upper)
    isEgg, maskNew = getMask(mask)

    cv2.imshow("mask", maskNew)
    cv2.waitKey(1)

    if isEgg:
        mean = cv2.mean(imgHSV, maskNew)
        # print(f"detected hue: {mean[0]}.")

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

def showTrackbars():
    def printTrackbars(printing=True):
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
        v_max = cv2.getTrackbarPos("Val Max", "Trackbars")

        if printing: print(h_min, h_max, s_min, s_max, v_min, v_max)

        return h_min, h_max, s_min, s_max, v_min, v_max

    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 640, 240)
    cv2.createTrackbar("Hue Min", "Trackbars", 0, 255, printTrackbars)
    cv2.createTrackbar("Hue Max", "Trackbars", 179, 255, printTrackbars)
    cv2.createTrackbar("Sat Min", "Trackbars", 58, 255, printTrackbars)
    cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, printTrackbars)
    cv2.createTrackbar("Val Min", "Trackbars", 113, 255, printTrackbars)
    cv2.createTrackbar("Val Max", "Trackbars", 255, 255, printTrackbars)

    return printTrackbars

def warpImg(img, points, w, h, pad=20):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    warpMatrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, warpMatrix, (w,h))
    imgWarp = imgWarp[pad:imgWarp.shape[0] - pad, pad:imgWarp.shape[1] - pad]

    return imgWarp

printTrackbars = showTrackbars()
