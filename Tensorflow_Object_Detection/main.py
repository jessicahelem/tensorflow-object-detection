# -*- coding: utf-8 -*-
"""
Based on article created by: 
@author: Alvaro Sebastian (www.sixthresearcher.com)
[Link]:(http://www.sixthresearcher.com/counting-blue-and-white-bacteria-colonies-with-python-and-opencv/)
"""
import cv2, os, imutils
import numpy as np

# Crop Image Function:



# Count Black Lines Function:
def count_lines(lower, upper, image_orig):
    # Final output
    image_contours = image_orig.copy()
    # copy of original image
    image_to_process = image_orig.copy()
    image_to_process = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2HSV)
    # initializes counter
    counter = 0
    # find the colors within the specified boundaries
    image_mask = cv2.inRange(image_to_process, lower, upper)
    cnts = cv2.findContours(image_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Here we get the contours:
    cnts = imutils.grab_contours(cnts)
    # loop over the contours individually
    for c in cnts:
        # if the contour is not sufficiently large, ignore it 
        if cv2.contourArea(c) < 5:
            continue
        # compute the Convex Hull of the contour [Optional, uncomment to see the change]
        # hull = cv2.convexHull(c)

        # prints contours in green color
        cv2.drawContours(image_contours, [c], 0, (0, 0, 255), 1)  # [c should be hull, if the previous line is used]
        # For each contour that is not too small increment by one
        counter += 1

    return counter, image_contours


# load the image
image_orig = cv2.imread('workspace/resultado/crop/fingerprint0000.png')

# DETECTING BY COLOR:

#lower = np.array([0, 0, 0])
#upper = np.array([0,  0, 0])

lower = np.array([-15, -10, -40])
upper = np.array([15, 10, 40])

counter, image_contours = count_lines(lower, upper, image_orig)

# Print the number of colonies of each color

print("{} linhas pretas".format(counter))

# Show the images

cv2.imshow('original', image_orig)

cv2.imshow('contornos', image_contours)

# Waiting for user input

cv2.waitKey(0)
