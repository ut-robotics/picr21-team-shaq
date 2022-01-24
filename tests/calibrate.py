import cv2
import numpy as np
import time
import json
import sys, os
from functools import partial
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config, vision
from threading import Thread

def update_range(edge, channel, value):
	"""
	Parameters:
		edge = "min" or "max"
		channel = 0, 1, 2 (H, S, V)
		value = new slider value
	"""
	filters[edge][channel] = value
	cap.active_processors[color].update_limits(filters)

def create_trackbars():
	win_name = "Set limits"
	cv2.namedWindow(win_name)
	cv2.createTrackbar("H lower", win_name, filters["min"][0], 255, partial(update_range, "min", 0))
	cv2.createTrackbar("S lower", win_name, filters["min"][1], 255, partial(update_range, "min", 1))
	cv2.createTrackbar("V lower", win_name, filters["min"][2], 255, partial(update_range, "min", 2))
	cv2.createTrackbar("H upper", win_name, filters["max"][0], 255, partial(update_range, "max", 0))
	cv2.createTrackbar("S upper", win_name, filters["max"][1], 255, partial(update_range, "max", 1))
	cv2.createTrackbar("V upper", win_name, filters["max"][2], 255, partial(update_range, "max", 2))
		
def main():
	global filters, cap, color
	try:
		color = sys.argv[1]
	except:
		print("Color input required:\n\npython calibrate.py {color name}")
		sys.exit(2)
	color_config = config.load("colors")
	if color not in color_config.keys():
		print(f"Color '{color}' not found in config")
		sys.exit(2)
		
	filters = color_config[color]
	create_trackbars()

	cap = vision.Capture((color,))
	cap.start_thread()

	win_name = f"Calibration for {color}"
	while True:
		#_, frame = cap.read() #(480, 640)
		frame = cap.get_color()
		if frame is None:
			continue
		#obj_mask = processor.produce_mask(cap.get_pf()) # ?[0:240, 0:320])
		obj_mask = cap.masks[color]
		if obj_mask is None:
			continue

		# cv2.circle(frame, (424, 280), 10, (0, 255, 0), 2)
		
		cv2.imshow("Set limits", frame)
		cv2.imshow(win_name, obj_mask)
		
		#mask = cv2.dilate(mask, kernel, iterations=2)

		k = cv2.waitKey(1) & 0xFF
		if k == ord("q"):
			print('Closing program')
			cap.stop()
			cv2.destroyAllWindows()
			config.update(color, filters) 
			break

if __name__ == "__main__":
	main()
