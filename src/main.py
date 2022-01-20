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
from Movement import Movement
from thrower_calc import Thrower

class State(Enum):
	FIND_BALL = 0
	ALIGN = 1
	THROW = 2
	MOVE_TO_BASE = 3
	QUIT = 6

def main():
	STATE = State.FIND_BALL
	target_set = False
	start_throw_timer = False
	start_search_timer = False
	align_timer = False
	persistence = 0
	frame_count = 0
	ball_centered = False
	aligned = False

	
	try:
		#colors = ("dark_green", "orange")
		BASKET = "magenta" # Hardcode for now
		colors = ("green", BASKET)

		# Initialize capture
		cap = Capture(colors)
		time.sleep(0.5) # ?
		detector = Detector(cap)
		thrower = Thrower()
		throw_speed = 0 # Testing purposes
		# --------------------------------------------------
		moveControl = Movement() # Includes Communication
		# --------------------------------------------------

		# Start the threads
		cap.start_thread()
		# cap.depth_active = True

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
					start_search_timer = False
					x, y = ball_coords
					# print(f"x: {x} y: {y}")
					detector.draw_point(frame, ball_coords, text="ball")
					y_base = moveControl.HEIGHT - y
					if y_base < 240:
						persistence += 1
						if persistence > 20: # x stable frames
							print("Found ball") # Ball is close, just stop for now
							moveControl.stop()
							STATE = State.ALIGN
							target_set = False
					else:
						persistence = 0
						#moveControl.move_at_angle(x, y)
						moveControl.chase_ball(x, y)
						pass

				else:
					# change robot viewpoint to find eligible ball
					current_time = time.time()
					if not start_search_timer: # Time out for when to move to base?
						start_time = time.time()
						start_search_timer = True
					elif current_time - start_time < 8: # No ball seen for x seconds
						start_search_timer = False
						target_set = False
						#STATE = State.MOVE_TO_BASE
						STATE = State.QUIT
					moveControl.spin_based_on_angle()
					pass
			
			elif STATE == State.MOVE_TO_BASE:
				# Use the baskets as localization references
				# Irrespective of the current one being used, drive towards the furthest one, while looking for balls?
				if not target_set:
					cap.update_targets(("green", "magenta", "blue"))
					target_set = True
					cap.depth_active = True

				ball_coords = detector.find_ball()
				if ball_coords != None:
					if frame_count > 10: # x stable frames
						frame_count = 0
						cap.depth_active = False
						target_set = False
						STATE = State.FIND_BALL
					else:
						frame_count += 1
						continue
				else:
					basket_coords_magenta = detector.find_basket("magenta")
					basket_coords_blue = detector.find_basket("blue")
					if basket_coords_magenta != None:
						x, y = basket_coords_magenta
						distance = cap.get_depth_from_point(x, y)
						if distance > 2:
							moveControl.move_at_angle(x, y)
						else:
							moveControl.spin_based_on_angle() # Too close, search for the basket that's further away
					elif basket_coords_blue != None:
						x, y = basket_coords_blue
						distance = cap.get_depth_from_point(x, y)
						if distance > 2:
							moveControl.move_at_angle(x, y)
						else:
							moveControl.spin_based_on_angle()
					else:
						moveControl.spin_based_on_angle() # No baskets seen, try to find one

			elif STATE == State.ALIGN:
				if not target_set:
					cap.update_targets(("green", BASKET)) # pick basket
					target_set = True
				# Start aligning the ball with the basket	
				basket_coords = detector.find_basket(BASKET)
				ball_coords = detector.find_ball()
				if basket_coords and ball_coords:
					detector.draw_point(frame, basket_coords, text="basket")
					detector.draw_point(frame, ball_coords, text="ball")
					# Perform aligning
					
					if moveControl.center_ball(ball_coords):
						aligned = moveControl.align_for_throw(ball_coords, basket_coords)
					else: pass

					if aligned:
						STATE = State.THROW
						cap.depth_active = True
						time.sleep(0.1) # depth activation
				else:
					# change robot viewpoint to find ball
					moveControl.rotate_based_on_angle(15)
					current_time = time.time()
					if not align_timer:
						start_time = time.time()
						align_timer = True
					elif current_time - start_time < 10:
						pass
					else:
						STATE = State.FIND_BALL
						align_timer = False

			elif STATE == State.THROW:
				# -----------------------------------------
				# For manual interpolation measurements
				# -----------------------------------------
				# basket_coords = detector.find_basket(BASKET)
				# if basket_coords == None:
				# 	continue
				# detector.draw_point(frame, basket_coords, text="basket")
				# x, y = basket_coords
				# basket_distance = cap.get_depth_from_point(x, y)
				# print(basket_distance)
				# moveControl.servo_speed = throw_speed
				# moveControl.sendSpeed([0, 0, 0])
				# -----------------------------------------
				basket_coords = detector.find_basket(BASKET)
				ball_coords = detector.find_basket("green")

				if basket_coords == None:
					# moveControl.spin_based_on_angle()
					continue
				x, y = basket_coords
				basket_distance = cap.get_depth_from_point(x, y)
				throw_speed = thrower.calc_throw_speed(basket_distance)
				if throw_speed is None: # Measurement in progress, will take average of x frames
					continue
				else:
					current_time = time.time()
					if not start_throw_timer:
						start_time = time.time()
						start_throw_timer = True
					elif current_time - start_time < 3: # Stop the throw after n seconds
						moveControl.servo_speed = throw_speed
						moveControl.forward(10) # Need to set it so that the robot adjusts while approaching, now will most prob miss
						# Experimental controlled approach
						#moveControl.attempt_throw(ball_coords, basket_coords)
						pass
					else:
						print("Used throw speed was", throw_speed)
						print("finito throwito")
						cap.depth_active = False
						STATE = State.QUIT
				
			elif STATE == State.QUIT:
				print('Closing program')
				moveControl.serial_link.stopThread = True # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				break

			cv2.imshow("View", frame)
			cv2.imshow("Balls", ball_mask)

			k = cv2.waitKey(1) & 0xFF
			if k == ord("q"):
				STATE = State.QUIT
			# elif k == ord("w"):
			# 	try:
			# 		throw_speed = int(input("Enter new desired throw speed: "))
			# 	except:
			# 		print("whoops")

	except Exception:
		print(traceback.format_exc())
		cv2.destroyAllWindows()
		cap.running = False

if __name__ == "__main__":
	main()
