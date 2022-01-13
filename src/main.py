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
from simp_detection import Detector, Filter
#from Detection import Detector, Filter
from Movement import Movement # should comm stay here?
from thrower_calc import Thrower

from enum import Enum

# Will implement states at some point
class State(Enum):
	FIND_BALL = 0
	ALIGN = 1
	THROW = 2
	QUIT = 6

def main():
	STATE = State.FIND_BALL
	target_set = False
	start_time_measure = False
	try:
		#colors = ("dark_green", "orange")
		BASKET = "blue" # Hardcode for now
		colors = ("green", BASKET)

		# Initialize capture
		cap = Capture(colors)
		detector = Detector(cap)
		thrower = Thrower()
		# --------------------------------------------------
		moveControl = Movement() # Includes Communication
		# --------------------------------------------------

		# Start the threads
		cap.start_thread()
		# detector.start_thread(cap) # This should probably be removed, procedural is better

		print(threading.active_count(), " are alive")
		print(threading.enumerate())

		while True:
			# Read capture and detector
			frame = cap.get_color()
			if frame is None:
				continue

			if STATE == State.FIND_BALL:
				if not target_set:
					cap.update_targets(("green",))
					target_set = True # Prevent constant updating?
				ball_mask = cap.masks["green"]
				if ball_mask is None: continue
				
				ball_coords = detector.find_ball(view=frame)
				if ball_coords != None: # If there is an eligible ball
					x, y = ball_coords
					print(f"x: {x} y: {y}")
					detector.draw_point(frame, ball_coords, text="ball")
					y_base = moveControl.HEIGHT - y
					if y_base < 250:
						print("rdy to throw") # Ball is close, just stop for now
						moveControl.stop()
					else:
						moveControl.move_at_angle(x, y)
						pass

				else:
					# change robot viewpoint to find eligible ball
					moveControl.spin_based_on_angle()
					pass

			elif STATE == State.ALIGN:
				if not target_set:
					detector.set_colors(("green", BASKET)) # pick basket
				# Start aligning the ball with the basket	
				basket_coords = detector.find_basket(BASKET)
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
					moveControl.rotate_based_on_angle()

			elif STATE == State.THROW:
				x, y = detector.find_basket(BASKET)
				basket_distance = cap.get_depth_from_point(x, y)
				throw_speed = thrower.calc_throw_speed(basket_distance)
				if throw_speed is None: # Measurement in progress, will take average of x frames
					continue
				else:
					current_time = time.time()
					if not start_time_measure:
						start_time = time.time()
						start_time_measure = True
					elif current_time - start_time < 5: # Stop the throw after n seconds
						moveControl.set_servo(throw_speed)
						moveControl.forward() # Need to set it so that the robot adjusts while approaching, now will most prob miss
						pass
					else:
						print("finito throwito")
						STATE = State.QUIT
				
			elif STATE == State.QUIT:
				print('Closing program')
				moveControl.serial_link.stopThread = True # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				break

			cv2.imshow("View", frame)
			#cv2.imshow("Balls", ball_mask)

			k = cv2.waitKey(1) & 0xFF
			if k == ord("q"):
				STATE = State.QUIT

	except Exception:
		print(traceback.format_exc())
		cv2.destroyAllWindows()
		cap.running = False

if __name__ == "__main__":
	main()
