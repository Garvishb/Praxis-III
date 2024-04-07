from ultralytics import YOLO
import cv2
import numpy
from inference_sdk import InferenceHTTPClient

# CLIENT = InferenceHTTPClient(
#     api_url="https://detect.roboflow.com",
#     api_key="vXDAUydBAlEIq1XHp17V"
# )

# result = CLIENT.infer("R_10686.jpg", model_id="neural_ocean/3")
# cv2.imshow("Result", result)

# Load the default, pretrained YOLOv8 Nano Model.
# This model gives bad results and I don't think it has many classes
model = YOLO(r"C:\Users\togar\Documents\UofT\Spring Term 2024\ESC204 - Praxis III\Praxis-III\Underwater-Waste-Detection-Using-YoloV8-And-Water-Quality-Assessment\models\Underwater_Waste_Detection_YoloV8\60_epochs_denoised.pt")

# This model just detects everything, need testing for solid waste
model2 = YOLO('yolov8m-seg.pt')
# cap = cv2.VideoCapture(0)
# success, img = cap.read()


# im2 = cv2.imread(r"C:\Users\togar\Documents\UofT\Spring Term 2024\ESC204 - Praxis III\Praxis-III\solid_waste_classification\O_12583.jpg")

# Test model on source and display source with results (bounding boxes). 
while True:
    res = model2.predict(source=0, show=True)
# print(res)
# res = numpy.array(res)
# cv2.imshow("YOLOv8", res)