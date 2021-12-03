import cv2
import time
import numpy as np
import threading
from copy import copy
import traceback
#----------------------------
import config
import Frame
from vision import Capture
from Detection import Detector, Filter
#from comm import Communication
from Movement import Movement # should comm stay here?

#variable for setting speeds of motors
set_speeds = [0,0,0,0]

def main():
	try:
		#colors = ("dark_green", "orange")
		colors = ("green", "black")
		# Initialize capture with a configured Pre-processor
		cap = Capture(Frame.Processor())
		detector = Detector(colors)
		coords = {}
		# --------------------------------------------------
		moveControl = Movement() # Include Communication
		moveControl.speed = 8
		# --------------------------------------------------
		#comm_main = Communication()

		detector.start_thread(cap)
		cap.start_thread()

		print(threading.active_count(), " are alive")
		print(threading.enumerate())

		motor_speed = 4
		motor_speed_opposite = -motor_speed

		while True:
			# Read capture and detector
			frame = cap.get_color()
			detector_output = detector.output

			if frame is not None:
				for clr in colors:
					mask = detector_output[clr]["mask"]
					if mask is None: continue # Wait until detector is ready
					#cv2.imshow(f"Mask {clr}", mask)

					clr_cntrs = detector_output[clr]["cntrs"]
					if clr_cntrs:
						# If something is seen
						detector.draw_contours(frame, detector_output[clr]["cntrs"])
					else: # If detector has not detected anything for the specific color, then jump to the next one	
						continue

					# Remember to always calibrate before to get a clean, noiseless frame without false detections	
					if clr == "green":
						#point = detector.filter_contour("green", Filter.BY_Y_COORD)
						# Assume black is on
						ball_coords = detector.find_ball(frame)
						
						if ball_coords != None:
							x, y = ball_coords
							print(f"x: {x} y: {y}")
							detector.draw_point(frame, ball_coords)
							#moveControl.move_towards_ball(x, y)
						else:
							# No eligible balls, spin to find
							continue
							
					elif clr == "black":
						pass

				cv2.imshow("View", frame)

					# ==================================
					# if clr == "dark_green":
						# if coords[clr]:
						# 	coords_ball = coords[clr]
						# 	print("(x,y) coordinates of the ball: " + str(coords_ball))
						# 	if coords_ball[0] < 270:
						# 		print("turn left")
						# 		set_speeds = [motor_speed,0,motor_speed,0]
						# 	elif coords_ball[0] > 370:
						# 		print("turn right")
						# 		set_speeds = [0,motor_speed_opposite,motor_speed_opposite,0]
						# 	else:
						# 		if coords_ball[1] < 200:
						# 			print("go forwards")
						# 			set_speeds = [motor_speed,motor_speed_opposite,0,0]
						# 		elif coords_ball[1] > 280:
						# 			print("go backwards")
						# 			set_speeds = [motor_speed_opposite,motor_speed,0,0]
						# 		else:
						# 			print("stay here")
						# 			set_speeds = [0,0,0,0]
						# 	comm_main.state = 1
						# 	comm_main.incoming_speeds = set_speeds
						# else:
						# 	print("go forwards")
						# 	set_speeds = [motor_speed,motor_speed_opposite,0,0]
						# 	comm_main.state = 1
						# 	comm_main.incoming_speeds = set_speeds
							#print("stop")
							#comm_main.state = 0
					# Windows should generally not be created as they're significantly slowing down the execution.
					# Do not delete those lines though, they're useful for testing/debugging.
					#cv2.imshow(clr.title(), Frames[i])
					#cv2.imshow(f"Mask {clr}", masks[clr])

			k = cv2.waitKey(1) & 0xFF
			if k == ord("q"):
				print('Closing program')
				#comm_main.state = 2
				moveControl.serial_link.state = 2 # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				break

	except Exception:
		print(traceback.format_exc())
		cv2.destroyAllWindows()
		cap.running = False

if __name__ == "__main__":
	main()
