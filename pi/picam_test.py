import numpy as np
import cv2 as cv
import time
from picamera2 import Picamera2


camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()
# camera.resolution = (640, 480)
time.sleep(0.1)

while True:
    # image = np.empty((480, 640, 3), dtype=np.uint8)
    img = camera.capture_array()
    # print(img)
    # Convert the image to RGB (OpenCV uses BGR by default)
    cv.imshow('frame', img)
    cv.waitKey(1)
    # camera.close()