import cv2
import time
import numpy as np
from threading import Thread
from enum import Enum
from typing import Tuple, List
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

	FIND_BALL_COLORS = ("green", "orange", "white", "black")
	TRANSITION = ("black", "white", "orange")
	FIND_BASKET_COLORS = ("green", "blue")

	def __init__(self, clrs: Tuple[str, ...]):
		presets = config.load("cam")
		self.fps = presets["fps"]
		self.height = presets["height"]

		self.colorDict = config.load("colors") # load color lib
		#self.update_targets(clrs)
		self.processors = { c: Processor(self.colorDict[c]) for c in clrs }
		self.line_detectors = { c: Processor(self.colorDict[c]) for c in self.TRANSITION }
		# Can do one by one or multiple, the functionality is there, don't know about the performance or how useful this actually is
		self.active_processors = self.processors # Detect all inputs by default

		self.min_ball_area = 70
		self.min_basket_area = 200

		# Output, can be read by other modules:
		self.output = { clr: {"mask": None, "cntrs": None} for clr in self.colorDict }
		#self.output = { clr: {"mask": None, "cntrs": None} for clr in list(self.active_processors.keys())}
		# {"dark_green": {"mask": ..., "cntrs": ...}, ...}
		self.line_check_length = self.height - 150

	def update_targets(self, clrs: Tuple[str, ...]):
		# Create/Update Processor objects using respective color limits
		# self.processors = { c: Processor(self.colorDict[c]) for c in clrs }
		return
		
	def clear_colors(self):
		self.active_processors = {}
	
	def good_color(self, clr):
		if clr not in self.colorDict:
			print("Invalid color, whoops")
			return False
		return True
		
	def set_colors(self, clrs: Tuple[str, ...]):
		self.clear_colors()
		for clr in clrs:
			if self.good_color(clr):
				self.active_processors[clr] = self.processors[clr]
	
	def get_clr(self, clr):
		mask = self.output[clr]["mask"]
		if mask is None:
			return None # Wait until detector is ready
		clr_cntrs = self.output[clr]["cntrs"]
		return (mask, clr_cntrs)

	def get_contours(self, mask):
		cntrs = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # Contours always 2nd from end, no matter the opencv version
		if len(cntrs):
			return cntrs
		else: return None

	def ball_in_court(self, center_pt, frame, view):
		# Use a much simpler method of checking the column of pixels to see if an orange-white-black transition occurs, haha I retract this
		# Use a much, MUCH simpler method of thresholding white pixels, and taking their average, if the robot is outside of court then this doesn't work
		x, y = center_pt
		# --------------------------------------------------------
		# Take 10 pixel wide strip?
		column = frame[x-5:x+6, y:self.line_check_length]
		#print(column.shape)
		cv2.line(view, (x,y), (x,self.line_check_length), (255, 0, 255), 1)
		if len(column) == 0: # idk why it sometimes comes up empty
			return True
		line_y = int(self.line_pos(column, view))
		if line_y < y: # Line found above the ball (has smaller y position)
			return True
		else:
			self.draw_point(view, (x, line_y))
			return False
		
		#return not self.check_transition(column) # If the transition is not present, return True, a.k.a ball is in court
	
	def line_pos(self, column, view=None):
		processor = self.line_detectors["white"]
		pf_column = processor.pre_process(column)
		binary = processor.threshold(pf_column)
		line_position = np.nonzero(binary)[1]
		average_y = np.mean(line_position)
		if np.isnan(average_y):
			return self.height
		else:
			return average_y
		

	# def check_transition(self, column):
	# 	transition_avg = []
	# 	# Threshold the column, looking for line colors
	# 	for clr in self.TRANSITION:
	# 		try:
	# 			processor = self.line_detectors[clr]
	# 			binary = processor.threshold(column)
	# 			# Calculate the average position of the detected color pixels
	# 			target_positions = np.nonzero(binary)
	# 			average_y = np.mean(target_positions[1]) # pick y
	# 			transition_avg.append(average_y)
	# 		except:
	# 			print("check_transition error")
	# 			return
	# 	print(transition_avg)

	# 	# Check if order is correct(avg y values), is it even necessary?
	# 	largest = transition_avg[0]
	# 	for clr in transition_avg:
	# 		if np.isnan(clr): # color not detected
	# 			return False
	# 		elif clr < largest: # something out of order
	# 			return False
	# 		else:
	# 			largest = clr
	# 	# black -> white -> orange transition detected:
	# 	return True

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
			elif clr == "blue" or clr == "magenta":
				if target_area > self.min_basket_area:
					return self.contour_center(target)
				else:
					return None
			else:
				return self.contour_center(target)

	def find_ball(self, frame, view): # expect pre-processed frame
	
		cntrs = self.output["green"]["cntrs"]
		if cntrs:
			#cntrs = list(cntrs) # Convert to list for sort
			#cntrs.sort(key=self.contour_y) # Start checking balls for eligibility from the closest
			for cntr in cntrs:
				center_pt = self.contour_center(cntr) # Duplicates moments operation, how expensive is that?
				# If the ball exists and passes the "in_court" test
				if center_pt and self.ball_in_court(center_pt, frame, view):
					cntr_area = cv2.contourArea(cntr)
					if cntr_area > self.min_ball_area:
						return center_pt
			return None
		else:
			return None

	def find_basket(self, clr):
		ct_point = self.filter_contour(clr, Filter.BY_SIZE)
		if ct_point != None:
			return ct_point
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

	def draw_point(self, frame, point, clr=(0, 0, 255), text=None):
		# 0 - input frame; 1 - draw origin; 2 - draw radius; 3 - color; 4 - line size
		cv2.circle(frame, point, 10, clr, 2)
		if text:
			cv2.putText(frame, text, point, cv2.FONT_HERSHEY_SIMPLEX, 1, clr, 2)

	def draw_contours(self, frame, contours):
		cv2.drawContours(frame, contours, -1, (0, 255, 0), 2) # -1 signifies drawing all cntrs

	def retrieve_closest(self, clr, view):
		closest = self.filter_contour(clr, Filter.BY_Y_COORD) # {x, y}
		#((x, y), radius) = cv2.minEnclosingCircle(cntr)
		#self.draw_point(view, closest, text="o_0")
		return closest

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
