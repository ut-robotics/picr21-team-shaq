import numpy as np
import math
import cv2

import Frame
import config

"""
Objective: Check if the ball is behind the line
Analysing the pixel values between two points in an image (the diagonal)
Point 1 = Ball
Point 2 = Robot base
d = The diagonal pixels
*************-***************
**Ball*****-*****************
*******d*E*******************
********Nd*******************
******I****d*****************
****L********d***************
***-********Robot************
**-**************************

If the ball (Point 1) is on the right side of the screen, the second diagonal will be taken

The diagonal values will be converted into a 1D array of color image values
These will be thresholded and checked for the color transition white -> black -> orange

First, check average position of white pixels, if there are none, assume ball is in court
Second, slice off the part of the array that comes after the average white index
Third, sample it for average black index, if there is none, assume ball is safe (how does this scenario come about?)
If the average black index is larger than that of white, check orange index, if that one is also larger, do not touch the ball, find next


"""

class LineSampler():

	TRANSITION = ("white", "black", "orange")

	def __init__(self):
		self.colorDict = config.load("colors")
		self.processors = { c: Frame.Processor(self.colorDict[c]) for c in self.TRANSITION }
		presets = config.load("cam")
		self.WIDTH = presets["width"]
		self.robot_ref_point = presets["height"] - 100 # arbitrary lift
		self.x_center = self.WIDTH / 2

	def get_diagonal(self, frame, ball_coords):
		x, y = ball_coords
		if x > self.x_center:
			# Reverse the polarity, collapse does it again
			frame = np.fliplr(frame)
			x = self.WIDTH - x

		sub_rec = frame[x:self.x_center + 1][y:self.robot_ref_point + 1]
		diagonal = sub_rec.diagonal()
		return diagonal
		

	def get_samples(self, diagonal):
		# Use any of the processors to convert the colorspace requried for hsv thresholding:
		hsv_diagonal = self.processors["white"].bgr_to_hsv(diagonal)

		samples = {}
		for color in self.processors:
			binary = self.processors[color].threshold(hsv_diagonal)
			samples[color] = np.nonzero(binary)[1] # Will return the indices of non_zero elements
			# Can we get away with only using `y` coordinates?
			
		return samples

	def check_ball_in_court(self, frame, ball_coords):
		diagonal = self.get_diagonal(frame, ball_coords)
		samples = self.get_samples(diagonal)

		mean_white = np.mean(samples["white"])
		if mean_white < 3: # Noise margin?
			return True
		
		mean_black = np.mean(samples["black"])
		if mean_black < 3: # IDk what is this
			return True

		orange_slice = samples["orange"][int(mean_white):]
		mean_orange = np.mean(orange_slice)

		white_below_black = (mean_white > mean_black)
		black_below_orange = (mean_black > mean_orange)

		if white_below_black and black_below_orange:
			return False
		else:
			return True
