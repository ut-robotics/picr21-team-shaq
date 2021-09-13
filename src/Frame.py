import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, List
"""

"""
@dataclass
class Processor:
    color_limits: Dict[str, List[int]]
    kernel: int = 5

    def process_frame(self, frame):
        blur = cv2.blur(frame, (self.kernel, self.kernel))
        frameHSV = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        lowerLimits = np.array(self.color_limits["min"]) # Assume single color input
        upperLimits = np.array(self.color_limits["max"])
        thresholded = cv2.inRange(frameHSV, lowerLimits, upperLimits)
        #closing = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
        inverted = cv2.bitwise_not(thresholded)

        return inverted