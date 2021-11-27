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

class Filter(Enum):
	BY_SIZE = 1
	BY_Y_COORD = 2

class Detector:

	def __init__(self, clrs: Tuple[str, ...]):
		presets = config.load("cam")
		self.fps = presets["fps"]

		self.colorDict = config.load("colors") # load color lib
		#self.update_targets(clrs)
		self.processors = { c: Processor(self.colorDict[c]) for c in clrs }
		# Can do one by one or multiple, the functionality is there, don't know about the performance or how useful this actually is
		self.active_processors = self.processors # Detect all inputs by default

		self.min_ball_area = 200
		self.min_basket_area = 200

		# Output, can be read by other modules:
		self.output = { clr: {"mask": None, "cntrs": None} for clr in self.colorDict }
		#self.output = { clr: {"mask": None, "cntrs": None} for clr in list(self.active_processors.keys())}
		# {"dark_green": {"mask": ..., "cntrs": ...}, ...}

	def update_targets(self, clrs: Tuple[str, ...]):
		# Create/Update Processor objects using respective color limits
		# self.processors = { c: Processor(self.colorDict[c]) for c in clrs }
		return
	def clear_colors(self):
		self.active_processors = []
	def add_color(self, clr):
		if clr not in self.colorDict:
			print("Invalid color")
			return
		self.active_processors.append(self.processors[clr])
	def remove_color(self, clr):
		if clr not in self.colorDict:
			print("Invalid color")
			return
		try:
			self.active_processors.remove(self.processors[clr])
		except:
			print(f"{clr} was not active")

	def get_contours(self, mask):
		cntrs = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # Contours always 2nd from end, no matter the opencv version
		if len(cntrs):
			return cntrs
		else: return None

	def largest_contour(self, frame):
		cntrs = self.get_contours(frame)
		if cntrs:
			largest = max(cntrs, key=cv2.contourArea)
			#print(cv2.contourArea(largest))
			if cv2.contourArea(largest) > self.min_ball_area:
				return largest
			else:
				return None

	def filter_contour(self, clr, method):
		# Filter a single contour using the output of the detection thread
		cntrs = self.output[clr]["cntrs"] 
		if cntrs:
			if method == Filter.BY_SIZE:
				target = max(cntrs, key=cv2.contourArea) # Filter based on the ball size, presumably the largest one is also the closest

			elif method == Filter.BY_Y_COORD:
				target = max(cntrs, key=self.contour_y) # Filter based on the largest y coordinate (closest to the robot)
			else:
				raise ValueError("Expected a method of type Filter.{METHOD}")
			if cv2.contourArea(target) > self.min_ball_area:
				return self.contour_center(target)
			else:
				return None
	
	def contour_y(self, cntr):
		M = cv2.moments(cntr)
		if M["m00"] > 0:
			cy = int(M["m01"] / M["m00"])
			return cy
		else: return 0
	def contour_x(self, cntr):
		M = cv2.moments(cntr)
		if M["m00"] > 0:
			cx = int(M["m10"] / M["m00"])
			return cx
		else: return 0

	def contour_center(self, cntr):
		M = cv2.moments(cntr) # https://theailearner.com/tag/image-moments-opencv-python/
		if M["m00"] > 0:
			cx = int(M["m10"] / M["m00"])
			cy = int(M["m01"] / M["m00"])
			return (cx, cy)
		else:
			return None

	def draw_point(self, frame, point):
		# 0 - input frame; 1 - draw origin; 2 - draw radius; 3 - color; 4 - line size
		cv2.circle(frame, point, 10, (0, 0, 255), 2)
	def draw_contours(self, frame, contours):
		cv2.drawContours(frame, contours, -1, (0, 255, 0), 2) # -1 signifies drawing all cntrs

	def draw_closest(self, clr, frame):
		closest = self.filter_contour(clr, Filter.BY_Y_COORD) # {x, y}
		if closest is None:
			return None
		#cntr = self.largest_contour(self.color_masks[clr])
		#if cntr is None: return
		#((x, y), radius) = cv2.minEnclosingCircle(cntr)
		#center = self.contour_center(cntr)
		self.draw_point(frame, point)
		return


	def main(self):
		#Processor = Frame.Processor(self.color_range)
		wait_time = 1 / self.fps
		while True:
			# Probably can move the preprocessing here, instead of having it in capture, but what does it matter, hehe
			frame = self.cap.get_pf() #expect pre_thresh frame, need to implement standby until new frame arrives?
			if frame is None: continue
			# Threshold all the colors required, create output
			for color, processor in self.active_processors.items():
				thresholded = processor.Threshold(frame) # Benchmarked at 0.0014
				self.output[color]["mask"] = thresholded
				self.output[color]["cntrs"] = self.get_contours(thresholded) # will return None if nothing found
			time.sleep(wait_time) # primitive sync

	def start_thread(self, cap):
		self.cap = cap # get ref to capture class for frame collection
		return Thread(name="Detection", target=self.main, daemon=True).start()


def main():
	return


if __name__ == "__main__":
	main()
