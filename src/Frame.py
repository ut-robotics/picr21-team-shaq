import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, List

"""
	Returns a frame masked for specific color, can be used for object detection
	All image pre-processing is done here
"""


#@dataclass   
class Processor:
	#color_limits: Dict[str, List[int]]
	#kernel: int = 5
	"""
	color_limits = { "min" || "max": limits list[int] }
	"""
	default = {"min": [11, 40, 66], "max": [22, 214, 224]}

	def __init__(self, color_limits=default):    
		self.update_limits(color_limits)

	def update_limits(self, new_limits):
		self.lowerLimits = np.array(new_limits["min"])
		self.upperLimits = np.array(new_limits["max"])

	def blur(self, frame, kernel=3):
		blur = cv2.blur(frame, (kernel, kernel))
		return blur
	
	def bgr_to_hsv(self, frame):
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		return hsv

	def morph_open(self, frame, kernel=5):
		opened = cv2.morphologyEx(frame, cv2.MORPH_OPEN, np.ones((kernel, kernel), np.uint8))
		return opened

	def morph_close(self, frame, kernel=5):
		closed = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, np.ones((kernel, kernel), np.uint8))
		return closed

	def threshold(self, frame):
		thresholded = cv2.inRange(frame, self.lowerLimits, self.upperLimits)
		return thresholded

	def pre_process(self, frame):
		operations = [
			self.blur,
			self.bgr_to_hsv
		]
		for operation in operations:
			frame = operation(frame)       
		return frame

	def Threshold(self, frame):
		operations = [
			self.threshold,
			self.morph_close # Thresholding mandatory, requires binary img
		]
		# Loop through all image processing operations and apply them
		for operation in operations:
			frame = operation(frame)   
		return frame

	def process_frame(self, frame):
		return self.Threshold(self.pre_process(frame))


def test():
	return
