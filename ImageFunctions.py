import cv2
import numpy as np

def warpImg(img, points, w, h, pad=20):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    warpMatrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, warpMatrix, (w,h))
    imgWarp = imgWarp[pad:imgWarp.shape[0] - pad, pad:imgWarp.shape[1] - pad]

    return imgWarp

def getEggColour(img, useSliders = False, takepic = 0, pictexEggcolor="None"):
    # Step 1: Convert the image to HLS (Hue, Light, Saturation) colourspace
    imgHLS = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)

    # Step 2: retrieve upper and lowerbound in HLS colourspace
    if useSliders:
        # Use values taken from the trackbars.
        h_min, h_max, l_min, l_max, s_min, s_max, A_min = printTrackbars(printing=False)
        lower = np.array([h_min, l_min, s_min])
        upper = np.array([h_max, l_max, s_max])
    else:
        # Only use default values
        lower = np.array([0, 58, 113])
        upper = np.array([179, 255, 255])
        A_min = 661

    # Step 3: pull an HSL 'in range' mask
    mask = cv2.inRange(imgHLS, lower, upper)

    # Step 4: 'refining' the egg mask, and determining the presence of an egg.
    isEgg, refinedMask = refineMask(mask, minArea=A_min)

    # Bonus step 1: displaying the mask
    if useSliders:
        cv2.imshow("mask", mask)
        cv2.imshow("refined mask", refinedMask)
        cv2.waitKey(1)

        if takepic > 0:
            cv2.imwrite(f"Output/{pictexEggcolor}mask{takepic}.jpg", mask)
            cv2.imwrite(f"Output/{pictexEggcolor}refinedMask{takepic}.png", refinedMask)

    # Step 5: if no egg is present, exit the function.
    if not isEgg:
        return "None", 0

    # Step 6: take the mean of the HLS picture, using the refined mask
    mean = cv2.mean(imgHLS, refinedMask)

    # Step 7: Determine the colour of the egg by comparing distance to hue setpoints
    colourNames = ["yellow", "blue", "red"]
    colourHues = [9, 109, 165]

    closestColourIndex = 0
    for i in range(len(colourHues)):
        if abs(colourHues[i] - mean[0]) < abs(colourHues[closestColourIndex] - mean[0]):
            closestColourIndex = i

    # Bonus step 2: Displaying the pixels taken into account when taking the mean, and showing the results.
    if useSliders:
        maskedegg = cv2.bitwise_and(img, img, mask=refinedMask)
        outputTxt = []

        outputTxt.append("Mean Hue = " + str(int(mean[0])))
        outputTxt.append("Mean Light = " + str(int(mean[1])))
        outputTxt.append("Mean Sat = " + str(int(mean[2])))
        outputTxt.append("Colour is " + colourNames[closestColourIndex])

        for i, txt in enumerate(outputTxt):
            cv2.putText(maskedegg, txt, (10, 20 + 20*i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 2)

        cv2.imshow("masked egg", maskedegg)
        cv2.waitKey(1)

        if takepic > 0:
            cv2.imwrite(f"{pictexEggcolor}Output/maskedEgg{takepic}.png", maskedegg)

    return colourNames[closestColourIndex], int(mean[0])

def refineMask(mask, minArea=1000):
    # Step 1: Finding all contours in image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 2: filtering the contours by minimum area size
    finalContours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea:
            peri = cv2.arcLength(contour, True)
            # approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
            finalContours.append([area, contour])

    # Step 3: sorting the contours by area size, so the biggest one
    # (presumably the egg) is the first element
    finalContours = sorted(finalContours, key=lambda x: x[0], reverse=True)

    # Step 4: if no egg is present, exit the function
    if len(finalContours) == 0:
        # No egg in the picture
        return False, mask

    # Step 5: making a new mask out of the contour approximation
    h, w = mask.shape[:2]
    maskNew = np.zeros((h, w), np.uint8)
    maskNew = cv2.fillPoly(maskNew, [finalContours[0][1]], 255)

    # # Step 5.5: Filling in the new contour-based mask
    # im_floodfill = maskNew.copy()
    # maskk = np.zeros((h + 2, w + 2), np.uint8) # for some reason, cv2.floodfill needs this
    # cv2.floodFill(im_floodfill, maskk, (0, 0), 255)
    # im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    # maskNew = maskNew | im_floodfill_inv

    # Step 6: erode the mask a little
    trueMask = cv2.erode(maskNew, np.ones([3,3], dtype=np.uint8), iterations=4)

    return True, trueMask


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

printTrackbars = showTrackbars()
