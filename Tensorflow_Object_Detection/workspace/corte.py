import cv2

image = cv2.imread('resultado/fingerprint0000.png')
y = 181
x = 86
h = 167
w = 199
crop = image[y:y+h, x:x+w]
cv2.imshow('Image', crop)
cv2.imwrite('corte.png',crop)
cv2.waitKey(0)
