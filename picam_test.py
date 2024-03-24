import numpy as np
import cv2 as cv
import time
from picamera2 import PiCamera2


camera = PiCamera2()
camera.resolution = (640, 480)
time.sleep(0.1)


image = np.empty((480, 640, 3), dtype=np.uint8)
camera.capture(image, 'bgr')

# Convert the image to RGB (OpenCV uses BGR by default)
# image_rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
cv.imshow('frame', image)
camera.close()