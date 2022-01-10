import cv2
import time
import numpy as np
from threading import Thread
from enum import Enum
from typing import Tuple, List

from Frame import Processor
import config


"""
All intelligent computer vision related stuff goes in here

Log:
    - Removed the separate Detection thread
"""

class Filter(Enum):
	BY_SIZE = 1
	BY_Y_COORD = 2

class Detector:

	FIND_BALL_COLORS = ("green", "orange", "white", "black")
	TRANSITION = ("black", "white", "orange")
	FIND_BASKET_COLORS = ("green", "blue")

	def __init__(self, cap):
        self.colorDict = config.load("colors")

        # Set noise thresholds
		self.min_ball_area = 50
		self.min_basket_area = 200

        self.cap = cap
        # self.contours = {}

	def get_contours(self, mask):
		cntrs = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # Contours always 2nd from end, no matter the opencv version
		if len(cntrs):
			return cntrs
		else: return None
	
    def size_filter(self, clr, cntr):
        area = cv2.contourArea(cntr)
        if clr == "green":
            if area > self.min_ball_area:
                return True
            else:
                return False
        elif clr in ["blue", "magenta"]:
            if area > self.min_basket_area:
                return True
            else:
                return False

	def filter_contour(self, cntrs, clr, method):
        if method == Filter.BY_SIZE:
            target = max(cntrs, key=cv2.contourArea) # Filter based on the ball size, presumably the largest one is also the closest
        elif method == Filter.BY_Y_COORD:
            target = max(cntrs, key=self.contour_y) # Filter based on the largest y coordinate (closest to the robot)
        else:
            raise ValueError("Expected a method of type Filter.{METHOD}")

        if self.size_filter(clr, target_area):
            return self.contour_center(target)
        else: return None

    def retrieve_closest(self, cntrs, clr, view):
		closest = self.filter_contour(cntrs, Filter.BY_Y_COORD) # {x, y}

		#((x, y), radius) = cv2.minEnclosingCircle(cntr)
		#self.draw_point(view, closest, text="o_0")
        
		return closest # Will return None if nothing found

	def find_ball(self, view):
        mask = self.cap.masks["green"]
        cntrs = self.get_contours(mask)
        if cntrs:
            target = self.retrieve_closest(cntrs, "green", view)
            return target
        else:
            return None

        #````````````````````````````````````````````````
		# if cntrs:
		# 	cntrs = list(cntrs) # Convert to list for sort
		# 	cntrs.sort(key=self.contour_y) # Start checking balls for eligibility from the closest
		# 	for cntr in cntrs:
		# 		center_pt = self.contour_center(cntr) # Duplicates moments operation, how expensive is that?
		# 		# If the ball exists and passes the "in_court" test
		# 		if center_pt: # and self.ball_in_court(center_pt, frame, view): # drop line detection for now I'm done
		# 			cntr_area = cv2.contourArea(cntr)
		# 			if cntr_area > self.min_ball_area:
		# 				return center_pt
		# 	return None
		# else:
		# 	return None

	def find_basket(self, mask):
		ct_point = self.filter_contour(mask, Filter.BY_SIZE)
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