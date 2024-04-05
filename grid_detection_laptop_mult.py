import numpy as np
import cv2 as cv
import time
import serial
import math

# New idea:
# Get the bounding box of the surface       
# Get the coordinates of the origin of the bounding box (left bottom corner) in camera frame
# Get a transformation matrix from camera frame to the surface frame
# Apply the transformation matrix to the coordinates of the recyclable garbage
# Calculate where it lies in the in the grid (might need a pixel to inch conversion?)


class GirdDetect():
    def __init__(self):
        self.cap = cv.VideoCapture(1)

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
            surface_coordinates = self.get_contours(canny, img_copy)
            if cv.waitKey(1) == ord('s'): # press q to exit  
                print("Surface coordinates: ", surface_coordinates)
                # print("Point Coordinates", point_coordinates)
                if surface_coordinates: # if surface is detected
                    point_coordinates = self.select_area_in_image(img_roi)
                    print("Point Coordinates: ", point_coordinates)
                       
                    pc_surface = self.transform_to_surface(surface_coordinates, point_coordinates) # Point Coordinates in surface frame
                    print("Point Coordinates in surface frame: ", pc_surface)
                    
                    grid_cell = self.get_block(pc_surface)
                    print("Grid cell: ", grid_cell)
                    send = True
                    if send == True:
                        port = "COM19"
                        baudrate = 9600
                        serial_connection = serial.Serial(port, baudrate)
                        self.send_serial(grid_cell, serial_connection)
                    
                else:
                    print("No surface detected")
                
                         
            # Display the resulting frame
            cv.imshow('contoured_img', img_copy)
            if cv.waitKey(1) == ord('q'): # press q to exit
                break     

        # When everything done, release the capture
        self.cap.release()
        cv.destroyAllWindows()
        
    def get_contours(self, img, img_copy):
        contours, hierarchy = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # boxes = {}
        # i = 0
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
                surface_coordinates = [x, y, w, h]
                # x and y are pixel coordinates, top down (the origin is at top left of the image)
                # w and h are width and height
                # rectangle vertices: (x, y); (x+w, y); (x, y+h); (x+w, y+h)
                
                if objCor == 4:
                    # Centre of the bounding box                    
                    # cx = x + w // 2
                    # cy = y + h // 2
                    # boxes[i] = ([cx, cy])
                    # i+=1
                    print("Bounding box: ", x, y, w, h)
                    
                    cv.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2) # drawing the bounding box for a rectangle (grid)
                    cv.putText(img_copy, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                    cv.putText(img_copy, "Area: " + str(int(area)), (x + w + 20, y + 45), cv.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

                    return surface_coordinates
                else:
                    cv.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2) # drawing the bounding box for other shape (solid waste)
                # Adding text to the image
                # At this point, this code is by Co-Pilot so I don't even know what this text is showing
                
    
    def get_block(self, pc_surface):
        """Get the coordinates in the form of a 6X6 grid"""

        grid_coordinates = []
        for i in range(len(pc_surface)):
            coord = []
            grid_bs_x = (pc_surface[i][4] // 6) # grid block size x
            grid_bs_y = (pc_surface[i][5] // 6) # grid block size y
            print("grid_bs_y", grid_bs_y)
            print("pc_surface_y", pc_surface[i][3])
            x_num = math.ceil(pc_surface[i][2] / grid_bs_x)
            y_num = math.ceil(pc_surface[i][3] / grid_bs_y)
            print("Number of LEDs", x_num, y_num)
            
            x = pc_surface[i][0] // grid_bs_x
            y = pc_surface[i][1] // grid_bs_y
            # print("Grid block: ", x, y)
            for i in range(x_num):
                for j in range(y_num):
                    coord.append([x+i+1, y+j+1])
            grid_coordinates = grid_coordinates + coord
        return grid_coordinates
        
        
        
    def transform_to_surface(self, surface_coordinates, point_coordinates):
        # coodinates is in format [x, y, w, h]
        pc_surface = []
        for i in range(len(point_coordinates)):
            pc_surface.append([point_coordinates[i][0]-surface_coordinates[0], point_coordinates[i][1] - surface_coordinates[1], point_coordinates[i][2], point_coordinates[i][3], surface_coordinates[2], surface_coordinates[3]])
        return pc_surface
        
    
    def select_area_in_image(self, img):
        """Select an area in the image to get the coordinates of the point in the image"""
        point_coordinates = []
        point_coordinates = cv.selectROIs("Select ROI", img, fromCenter=False, showCrosshair=True)
        
        # print("Selected Area:", point_coordinates)
        mid = []
        coord = []
        for i in range(len(point_coordinates)):
            # print(point_coordinates[i])
            mid.append([((point_coordinates[i][0] + (point_coordinates[i][2] // 2))), ((point_coordinates[i][1] + (point_coordinates[i][3]) // 2)), point_coordinates[i][2], point_coordinates[i][3]])
            coord.append([point_coordinates[i][0], point_coordinates[i][1], point_coordinates[i][2], point_coordinates[i][3]])
        # mid_x = []
        # mid_y = []
        # for i in range(len(point_coordinates)):
        #     mid_x.append((point_coordinates[i][0] + point_coordinates[i][2]) // 2)
        #     mid_y.append((point_coordinates[i][1] + point_coordinates[i][3]) // 2)
        # print(coord)
        # print(mid)
        return coord
        
    def send_serial(self, grid_cell, serial_connection):
        """Transform grid coordinate to bottom left origin (6-y) and then change it to 36bit binary: 
        000000 000000 000000 000000 000000 000000 where it goes 
        (1,1), (2,1), (3,1)....(6, 1), (1, 2), (2, 2)....(6, 6)"""
        
        binary_string = "0" * 36
        for i in range(len(grid_cell)):
            grid_cell[i][1] = 7 - grid_cell[i][1]
        
            binary_string = self.coordinate_to_binary(grid_cell[i], binary_string)
        
        for i in range(0, len(binary_string), 6):
            print(binary_string[i:i+6])
        # print(binary_string)
        packet = bytearray()
        for i in range(0, len(binary_string), 6):
            byte = binary_string[i:i+6]
            packet.append(int(byte, 2))
            print(packet)
        
        print("Packet: ", packet)
        serial_connection.write(bytes('<', 'utf-8')) 
        serial_connection.write(packet)
        serial_connection.write(bytes('>', 'utf-8'))
        print("Data sent")
        serial_connection.close()
    
    def coordinate_to_binary(self, grid_cell, binary_string):
        """Convert the grid cell to 36bit binary"""
        # print(binary_string[:(grid_cell[0] + (grid_cell[1]-1)*6 - 1)])
        # print(binary_string[grid_cell[0] + (grid_cell[1]-1)*6:])
        binary_string = binary_string[:(grid_cell[0] + (grid_cell[1]-1)*6 - 1)] + "1" + binary_string[grid_cell[0] + (grid_cell[1]-1)*6:]
        return binary_string
        
        
    
    def show_image(self, img, name): # havn't figured this out yet
        cv.imshow(name, img)
        if cv.waitKey(1) == ord('q'): # press q to exit
            return False
                



if __name__ == "__main__":
    gd = GirdDetect()
    gd.detect()