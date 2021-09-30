import cv2
import time
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config, Frame

cap = cv2.VideoCapture(0)
Processor = Frame.Processor()
timeArray = []

for _ in range(100):
    _, frame = cap.read() #(480, 640)
    pf = Processor.pre_process(frame)

    e1 = cv2.getTickCount()
    #Measurable code block
    #--------------------------------
    color_mask = Processor.Threshold(pf)
    #--------------------------------
    e2 = cv2.getTickCount()
    time = (e2 - e1)/ cv2.getTickFrequency()   
    timeArray.append(time)

print("Operation time", sum(timeArray) / len(timeArray))
cap.release()
cv2.destroyAllWindows()