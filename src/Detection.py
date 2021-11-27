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

	
	def get_borderpoints(self):
		# https://docs.opencv.org/3.4/da/d22/tutorial_py_canny.html
		# line = self.filter_contour("black", Filter.BY_SIZE)
		
		# Assume "black" is enabled, should implement independence
		cntrs = self.output["black"]["cntrs"]

		list_of_pts = [] 
		for cntr in cntrs:
			list_of_pts += [pt[0] for pt in cntr] # combine all detected points
		list_of_pts = np.array(list_of_pts)
		# print(list_of_pts[0], list_of_pts[1])
		# line = np.concatenate(cntrs) # Add all together in case of breaks in the line
		# line_pixels = cv2.findNonZero(line) # Returns coordinates of the line pixels

		# Find min y, min x and max x (Translating into Top, Left and Right), Indexes:
		top = np.argmin(list_of_pts[:,1])
		left = np.argmin(list_of_pts[:,0])
		right = np.argmax(list_of_pts[:,0])

		points = {
			"top": list_of_pts[top],
			"left": list_of_pts[left],
			"right": list_of_pts[right],
		}
		return points
		#enclosure = cv2.minAreaRect(line_pixels)

	def ball_in_court(self, x, y, draw_frame=None):

		border_pts = self.get_borderpoints()
		topY = border_pts["top"][1]
		rightX = border_pts["right"][0]
		leftX = border_pts["left"][0]

		# Optionally draw on the frame
		if draw_frame is not None:
			for pt in border_pts:
				self.draw_point(draw_frame, border_pts[pt])
		
		if y > topY and x < rightX and x > leftX:
			return True
		else:
			return False

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

			target_area = cv2.contourArea(target)
			
			if clr == "green":
				if target_area > self.min_ball_area:
					return self.contour_center(target)
				else:
					return None
			else:
				return self.contour_center(target)
	
	def find_ball(self, draw_frame=None):
		cntrs = self.output["green"]["cntrs"]
		if cntrs:
			cntrs.sort(key=self.contour_y) # Start checking balls for eligibility from the closest
			for cntr in cntrs:
				x, y = self.contour_center(cntr) # Duplicates moments operation, how expensive is that?
				if self.ball_in_court(x, y, draw_frame):
					cntr_area = cv2.contourArea(cntr)
					if cntr_area > self.min_ball_area:
						return (x, y)
			return None
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
		#((x, y), radius) = cv2.minEnclosingCircle(cntr)
		self.draw_point(frame, closest)
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
