import cv2

image = cv2.imread('22_2.jpg')
y = 292
x = 199
h = 138
w = 86
crop = image[y:y+h, x:x+w]
cv2.imshow('Image', crop)
cv2.imwrite('corte.png',crop)
cv2.waitKey(0)





# cv2.rectangle(canvas, (10, 70), (90, 190), verde)
# cv2.imshow("Canvas", canvas)
# cv2.waitKey(0)
#
# #desenha o retângulo todo vermelho
# vermelho = (0, 0, 255)
# cv2.rectangle(canvas, (250, 50), (300, 125), vermelho, -1)
# cv2.imshow("Canvas", canvas)
# cv2.waitKey(0)
