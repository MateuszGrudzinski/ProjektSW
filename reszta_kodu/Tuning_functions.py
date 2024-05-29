import cv2
import numpy as np
def callback(x):
    pass
def Tablica_TH_tune(windowName,img):
    key = ord('o')
    ilowH = 0
    ihighH = 179

    ilowS = 0
    ihighS = 255
    ilowV = 100
    ihighV = 255

    cv2.createTrackbar('lowH', windowName, ilowH, 179, callback)
    cv2.createTrackbar('highH', windowName, ihighH, 179, callback)

    cv2.createTrackbar('lowS', windowName, ilowS, 255, callback)
    cv2.createTrackbar('highS', windowName, ihighS, 255, callback)

    cv2.createTrackbar('lowV', windowName, ilowV, 255, callback)
    cv2.createTrackbar('highV', windowName, ihighV, 255, callback)

    while key != ord('e'):

        ilowH = cv2.getTrackbarPos('lowH', windowName)
        ihighH = cv2.getTrackbarPos('highH', windowName)
        ilowS = cv2.getTrackbarPos('lowS', windowName)
        ihighS = cv2.getTrackbarPos('highS', windowName)
        ilowV = cv2.getTrackbarPos('lowV', windowName)
        ihighV = cv2.getTrackbarPos('highV', windowName)

        lower_hsv = np.array([ilowH, ilowS, ilowV])
        higher_hsv = np.array([ihighH, ihighS, ihighV])
        mask = cv2.inRange(img, lower_hsv, higher_hsv)

        cv2.imshow(windowName, mask)
        key = cv2.waitKey(100)