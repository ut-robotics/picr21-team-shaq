import cv2
import time
import numpy as np
import threading
from enum import Enum

# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Frame
import config

class Color(Enum):
    green = "green"
    blue = "blue"
    magenta = "magenta"
    orange = "orange"

class Detector:
    
    def __init__(self):
        self.min_ball_area = 30
        self.min_basket_area = 200
        self.color_config = config.load("colors")

    def largest_contour(self, frame):
        cntrs = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # Contours always 2nd from end, no matter the opencv version
        if len(cntrs) > 0:
            largest = max(cntrs, key=cv2.contourArea)
            return largest
        else:
            return None
    
    def contour_center(self, cntr):
        M = cv2.moments(cntr) # https://theailearner.com/tag/image-moments-opencv-python/
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
        else:
            return None

    def draw_entity(self, mask, frame):
        cntr = self.largest_contour(mask)
        if cntr is None: return
        #((x, y), radius) = cv2.minEnclosingCircle(cntr)
        center = self.contour_center(cntr)
        # 0 - input frame; 1 - draw origin; 2 - draw radius; 3 - color; 4 - line sizeq
        #cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
        cv2.circle(frame, center, 20, (0, 0, 255), 2)

def main():

    detector = Detector()
    Processor = Frame.Processor(detector.color_config[Color.green.name])
    #print(detector.color_config[Color.green.name])
    #detection_thread = Thread(target=detector, daemon=True)
    cap = cv2.VideoCapture(0)
    
    while True:
        _, frame = cap.read() #(480, 640)
        obj_mask = Processor.process_frame(frame)#[0:240, 0:320])
        #print(obj_mask)
        #contours = detector.get_contours(obj_mask)
        #print(contours)
        #print(detector.find_ball(contours))
        detector.draw_entity(obj_mask, frame)
        cv2.imshow("Hello", obj_mask)
        cv2.imshow("Output", frame)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            print('Closing program')
            cap.release()
            cv2.destroyAllWindows()
            break
        #time.sleep(1)
if __name__ == "__main__":
    main()
