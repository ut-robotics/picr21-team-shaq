import cv2
import time
import numpy as np
from threading import Thread
from enum import Enum
from typing import Tuple
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Frame import Processor
import config
import vision


"""
All intelligent computer vision related stuff goes in here
"""

# class Color(Enum):
# 	green = "green"
# 	blue = "blue"
# 	magenta = "magenta"
# 	orange = "orange"
# detector.getgreencoords
# detector.getbluecoords
# detector.stopColor
# detector.startColor
# detector.setColor

class Detector:

	def __init__(self, clrs: Tuple[str, ...]):
		presets = config.load("cam")
		self.fps = presets["fps"]

		self.colorDict = config.load("colors") # load color lib
		self.update_targets(clrs)

		self.min_ball_area = 500
		self.min_basket_area = 200

		# Output:
		self.color_masks = {}

	def update_targets(self, clrs):
		# Create/Update Processor objects using respective color limits
		self.processors = { c: Processor(self.colorDict[c]) for c in clrs }

	def largest_contour(self, frame):
		cntrs = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # Contours always 2nd from end, no matter the opencv version
		if len(cntrs) > 0:
			largest = max(cntrs, key=cv2.contourArea)
			#print(cv2.contourArea(largest))
			if cv2.contourArea(largest) > self.min_ball_area:
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

	def draw_entity(self, c, frame):
		if not len(self.color_masks):
			print("Initializing...")
			return
		cntr = self.largest_contour(self.color_masks[c])
		if cntr is None: return
		#((x, y), radius) = cv2.minEnclosingCircle(cntr)
		center = self.contour_center(cntr)
		# 0 - input frame; 1 - draw origin; 2 - draw radius; 3 - color; 4 - line size
		#cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
		cv2.circle(frame, center, 20, (0, 0, 255), 2)
		return center

	def main(self):
		#Processor = Frame.Processor(self.color_range)
		wait_time = 1 / self.fps
		while True:
			# Probably can move the preprocessing here, instead of having it in capture
			frame = self.cap.get_pf() #expect pre_thresh frame, need to implement standby until new frame arrives?
			if frame is None: continue
			# Threshold all the colors required
			for color, processor in self.processors.items():
				self.color_masks[color] = processor.Threshold(frame) # Benchmarked at 0.0014
			time.sleep(wait_time) # primitive sync

	def start_thread(self, cap):
		self.cap = cap # get ref to capture class for frame collection
		return Thread(name="Detection", target=self.main, daemon=True).start()


def main():
	return


if __name__ == "__main__":
	main()
