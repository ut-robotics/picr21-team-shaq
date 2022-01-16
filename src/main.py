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
	QUIT = 6

def main():
	global STATE, target_set, start_time_measure, persistence, BASKET, cap, detector, thrower, throw_speed, moveControl, frame, ball_mask
	STATE = State.FIND_BALL
	target_set = False
	start_time_measure = False
	persistence = 0
	#colors = ("dark_green", "orange")
	BASKET = "magenta" # Hardcode for now
	colors = ("green", BASKET)

	try:

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
				find_ball()

			elif STATE == State.ALIGN:
				align()
			
			elif STATE == State.THROW:
				throw_state()

			elif STATE == State.QUIT:
				quit_state()
				break

			cv2.imshow("View", frame)
			#cv2.imshow("Balls", ball_mask)

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

def find_ball():
	global target_set, cap, ball_mask, frame, persistence, STATE
	if not target_set:
		cap.update_targets(("green",))
		target_set = True # Prevent constant updating?
	ball_mask = cap.masks["green"]

	if ball_mask is not None:
		ball_coords = detector.find_ball(view=frame)
		if ball_coords != None: # If there is an eligible ball
			x, y = ball_coords
			print(f"x: {x} y: {y}")
			detector.draw_point(frame, ball_coords, text="ball")
			y_base = moveControl.HEIGHT - y
			if y_base < 220:
				persistence += 1
				if persistence > 20: # x stable frames
					print("rdy to throw") # Ball is close, just stop for now
					moveControl.stop()
					STATE = State.ALIGN
					target_set = False
			else:
				persistence = 0
				moveControl.move_at_angle(x, y)

		else:
			# change robot viewpoint to find eligible ball
			moveControl.spin_based_on_angle()

def align():
	global target_set, cap, frame, moveControl, STATE
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
		aligned = moveControl.align_for_throw(ball_coords, basket_coords)
		if aligned:
			STATE = State.THROW
			cap.depth_active = True
			time.sleep(0.1) # depth activation
	else:
		# change robot viewpoint to find ball
		moveControl.rotate_based_on_angle(15)

def throw_state():
	global cap, thrower, throw_speed, start_time_measure, moveControl, STATE
	cap.depth_active = True
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
	#if basket_coords == None:
		# moveControl.spin_based_on_angle()
	if basket_coords != None:
		x, y = basket_coords
		basket_distance = cap.get_depth_from_point(x, y)
		throw_speed = thrower.calc_throw_speed(basket_distance)
		if throw_speed is not None: # Measurement in progress, will take average of x frames
			current_time = time.time()
			if not start_time_measure:
				start_time = time.time()
				start_time_measure = True
			elif current_time - start_time < 3: # Stop the throw after n seconds
				moveControl.servo_speed = throw_speed
				moveControl.forward(10) # Need to set it so that the robot adjusts while approaching, now will most prob miss
			else:
				print("Used throw speed was", throw_speed)
				print("finito throwito")
				cap.depth_active = False
				STATE = State.QUIT

def quit_state():
	global cap
	print('Closing program')
	moveControl.serial_link.stopThread = True # QUIT
	cap.running = False
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
