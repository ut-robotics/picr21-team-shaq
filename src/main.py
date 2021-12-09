import cv2
import time
import numpy as np
import threading
from enum import Enum
from copy import copy
import traceback
#----------------------------
import config
import Frame
from vision import Capture
from Detection import Detector, Filter
#from comm import Communication
from Movement import Movement # should comm stay here?

from enum import Enum

# Will implement states at some point
class State(Enum):
	FIND_BALL = 0
	ALIGN = 1
	THROW = 2
	QUIT = 6

#variable for setting speeds of motors
set_speeds = [0,0,0,0]

global STATE
STATE = State.FIND_BALL

def main():
	global STATE
	try:
		#colors = ("dark_green", "orange")
		BASKET = "blue" # Hardcode for now
		colors = ("green", BASKET)
		# Initialize capture with a configured Pre-processor
		cap = Capture(Frame.Processor())
		detector = Detector(colors)
		coords = {}
		# --------------------------------------------------
		moveControl = Movement() # Includes Communication
		moveControl.speed = 8
		# --------------------------------------------------
		#comm_main = Communication()

		detector.start_thread(cap) # This should probably be removed, procedural is better
		cap.start_thread()

		print(threading.active_count(), " are alive")
		print(threading.enumerate())

		motor_speed = 4
		motor_speed_opposite = -motor_speed

		while True:
			# Read capture and detector
			frame = cap.get_color()
			if frame is None:
				continue
			detector_output = detector.output

			if STATE == State.FIND_BALL:
				detector.set_colors( ("green",) )
				detected = detector.get_clr("green")
				if detected:
					mask, cntrs = detected
				else: continue
				if cntrs: # If something is seen
					detector.draw_contours(frame, cntrs)
					ball_coords = detector.find_ball(cap.get_pf(), view=frame)
					if ball_coords != None: # If there is an eligible ball
						x, y = ball_coords
						print(f"x: {x} y: {y}")
						detector.draw_point(frame, ball_coords, text="ball")
						y_base = moveControl.y_center - y
						if y_base < 50:
							print("<50, stopping") # Ball is close, just stop for now
							moveControl.serial_link.state = 0 # STOP
							STATE = State.QUIT
						else:
							#moveControl.move_at_angle(x, y)
							pass

					else:
						# change robot viewpoint to find eligible ball
						#moveControl.spin_based_on_angle()
						pass

				else:
					# change robot viewpoint to find ball
					#moveControl.spin_based_on_angle()
					pass

			elif STATE == State.ALIGN:
				moveControl.serial_link.state = 1 # Ready for movement

				# Start aligning the ball with the basket
				detector.set_colors(("green", BASKET)) # pick basket
				basket_coords= detector.find_basket(BASKET)
				ball_coords = detector.retrieve_closest("green")
				if basket_coords and ball_coords:
					detector.draw_point(frame, basket_coords, text="basket")
					detector.draw_point(frame, ball_coords, text="ball")
					# Perform aligning
					aligned = moveControl.align_for_throw(ball_coords, basket_coords)
					if aligned:
						STATE = State.QUIT
				else:
					# change robot viewpoint to find ball
					moveControl.spin_based_on_angle()

			elif STATE == State.THROW:
				pass
			
			elif STATE == State.QUIT:
				print('Closing program')
				moveControl.serial_link.state = 2 # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				pass

			cv2.imshow("View", frame)

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
