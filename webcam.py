import numpy as np
import cv2 as cv


class GirdDetect():
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
            
    def detect(self):
        while True:
            # Capture frame-by-frame
            success, img = self.cap.read()
            # if frame is read correctly success is True
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Our operations on the frame come here
            # Turn original image to canny
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(gray, (5, 5), 3)
            canny = cv.Canny(blur, 50, 50)
            cv.imshow('canny', canny) 
            
            img_copy = img.copy()
            img_roi = img.copy()
            # getting contours
            self.get_contours(canny, img_copy)
            
            
            if cv.waitKey(1) == ord('s'): # press q to exit
                self.select_area_in_image(img_roi)
                cv.imshow('roi', img_roi)

            
            
            # Display the resulting frame
            cv.imshow('contoured_img', img_copy)
            if cv.waitKey(1) == ord('q'): # press q to exit
                break     

        # When everything done, release the capture
        self.cap.release()
        cv.destroyAllWindows()
        
    def get_contours(self, img, img_copy):
        contours, hierarchy = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        boxes = {}
        i = 0
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > 1000:
                # Drawing contours on the copy of image
                cv.drawContours(img_copy, cnt, -1, (255, 0, 0), 3)
                peri = cv.arcLength(cnt, True) # getting the perimeter
                approx = cv.approxPolyDP(cnt, 0.02 * peri, True) # getting the number of corner points
                print(len(approx)) # number of corner points
                objCor = len(approx) # number of corner points
                x, y, w, h = cv.boundingRect(approx) # getting the bounding box
                print("Bounding box: ", x, y, w, h)
                
                if objCor == 4:
                    # Centre of the bounding box
                    
                    cx = x + w // 2
                    cy = y + h // 2
                    boxes[i] = ([cx, cy])
                    i+=1
                    cv.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2) # drawing the bounding box for a rectangle (grid)
                else:
                    cv.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2) # drawing the bounding box for other shape (solid waste)
                # Adding text to the image
                cv.putText(img_copy, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv.putText(img_copy, "Area: " + str(int(area)), (x + w + 20, y + 45), cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
    
    def select_area_in_image(self, img):
        x, y, w, h = cv.selectROI("Select ROI", img, fromCenter=False, showCrosshair=True)
        print(x, y, w, h)
        
                    
    
    def show_image(self, img, name): # havn't figured this out yet
        cv.imshow(name, img)
        if cv.waitKey(1) == ord('q'): # press q to exit
            return False
                
                
                
    
 
# New idea:
# Get the bounding box of the surface       
# Get the coordinates of the origin of the bounding box (left bottom corner) in camera frame
# Get a transformation matrix from camera frame to the surface frame
# Apply the transformation matrix to the coordinates of the recyclable garbage
# Calculate where it lies in the in the grid (might need a pixel to inch conversion?)



if __name__ == "__main__":
    gd = GirdDetect()
    gd.detect()