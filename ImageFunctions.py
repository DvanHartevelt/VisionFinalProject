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

        # erode the mask
        trueMask = cv2.erode(newnewMask, np.ones([3,3], dtype=np.uint8), iterations=4)

        return True, trueMask

def getEggColour(img, useSliders = False):
    imgHLS = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)

    if not useSliders:
        lower = np.array([0, 58, 113])
        upper = np.array([179, 255, 255])
        A_min = 1000
    else:
        h_min, h_max, l_min, l_max, s_min, s_max, A_min = printTrackbars(printing=False)
        lower = np.array([h_min, l_min, s_min])
        upper = np.array([h_max, l_max, s_max])

    mask = cv2.inRange(imgHLS, lower, upper)
    isEgg, maskNew = getMask(mask, minArea=A_min)

    if useSliders:
        cv2.imshow("mask", mask)
        cv2.imshow("maskNew", maskNew)
        cv2.waitKey(1)

    if isEgg:
        mean = cv2.mean(imgHLS, maskNew)
        # print(f"detected hue: {mean[0]}.")

        if useSliders:
            maskedegg = cv2.bitwise_and(img, img, mask=maskNew)
            outputTxt1 = "Mean Hue = " + str(int(mean[0]))
            outputTxt2 = "Mean Light = " + str(int(mean[1]))
            outputTxt3 = "Mean Sat = " + str(int(mean[2]))

            cv2.putText(maskedegg, outputTxt1, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 2)
            cv2.putText(maskedegg, outputTxt2, (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 2)
            cv2.putText(maskedegg, outputTxt3, (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 2)

            cv2.imshow("masked egg", maskedegg)
            cv2.waitKey(1)

        colourNames = ["red", "yellow", "green", "blue", "red"]
        colourHues = [18, 25, 82, 94, 180]

        closestColourIndex = 0
        for i in range(len(colourHues)):
            if abs(colourHues[i] - mean[0]) < abs(colourHues[closestColourIndex] - mean[0]):
                closestColourIndex = i

        # print(f"The colour of this egg is: {colourNames[closestColourIndex]}, with an area of {cv2.countNonZero(maskNew)}.")
        return colourNames[closestColourIndex], mean
    else:
        # print("No egg in field of view")
        return "None", 0

def showTrackbars():
    def printTrackbars(printing=False):
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        l_min = cv2.getTrackbarPos("Lit Min", "Trackbars")
        l_max = cv2.getTrackbarPos("Lit Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        A_min = cv2.getTrackbarPos("Area Min", "Trackbars")


        if printing: print(h_min, h_max, l_min, l_max, s_min, s_max, A_min)

        return h_min, h_max, l_min, l_max, s_min, s_max, A_min

    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 640, 240)
    cv2.createTrackbar("Hue Min", "Trackbars", 0, 360, printTrackbars)
    cv2.createTrackbar("Hue Max", "Trackbars", 360, 360, printTrackbars)
    cv2.createTrackbar("Lit Min", "Trackbars", 51, 255, printTrackbars)
    cv2.createTrackbar("Lit Max", "Trackbars", 171, 255, printTrackbars)
    cv2.createTrackbar("Sat Min", "Trackbars", 34, 255, printTrackbars)
    cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, printTrackbars)
    cv2.createTrackbar("Area Min", "Trackbars", 661, 2000, printTrackbars)


    return printTrackbars

def warpImg(img, points, w, h, pad=20):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    warpMatrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, warpMatrix, (w,h))
    imgWarp = imgWarp[pad:imgWarp.shape[0] - pad, pad:imgWarp.shape[1] - pad]

    return imgWarp

printTrackbars = showTrackbars()
