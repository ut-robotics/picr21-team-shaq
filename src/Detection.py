import cv2
import time
import numpy as np
from threading import Thread
from enum import Enum
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Frame
import config
import vision

class Color(Enum):
    green = "green"
    blue = "blue"
    magenta = "magenta"
    orange = "orange"

class Detector:
    
    def __init__(self, color_range):
        self.min_ball_area = 30
        self.min_basket_area = 200
        self.color_range = color_range
        self.color_mask = None

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

    def draw_entity(self, frame):
        if self.color_mask is None: return
        cntr = self.largest_contour(self.color_mask)
        if cntr is None: return
        #((x, y), radius) = cv2.minEnclosingCircle(cntr)
        center = self.contour_center(cntr)
        # 0 - input frame; 1 - draw origin; 2 - draw radius; 3 - color; 4 - line size
        #cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
        cv2.circle(frame, center, 20, (0, 0, 255), 2)
    
    def main(self, lock):
        Processor = Frame.Processor(self.color_range)
        while True:
            lock.acquire()
            frame = self.cap.get_pf() #expect pre_thresh frame, need to implement standby until new frame arrives?
            lock.release()
            if frame is None: continue
             # Set it up for drawing function, which reads the class var:
            self.color_mask = Processor.Threshold(frame)
            #time.sleep(1)
            #self.draw_entity(frame=frame) #?
  
    def start_thread(self, cap, lock):
        self.cap = cap # create source for frames
        return Thread(target=self.main, daemon=True, args=(lock,)).start()


def main():
    return


if __name__ == "__main__":
    main()
