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
from client import Client
import queue

class State(Enum):
	FIND_BALL = 0
	ALIGN = 1
	THROW = 2
	MOVE_TO_BASE = 3
	STOP = 5
	QUIT = 6

def main():
	#STATE = State.FIND_BALL
	#STATE = State.MOVE_TO_BASE
	STATE = State.STOP # During the game this would be the default state until robot receives "start" signal directed to it.
	target_set = False
	start_throw_timer = False
	start_search_timer = False
	align_timer = False
	persistence = 0
	frame_count = 0
	ball_centered = False
	aligned = False
	frame = None

	# "Shaq" for now
	robot_name = "Shaq"
	referee_ip = "192.168.3.11"
	referee_port = "8765"
	referee_data = None
	recv_queue = queue.Queue()
	
	try:
		#colors = ("dark_green", "orange")
		#BASKET = "magenta" # Hardcode for now
		#colors = ("green", "magenta")
		BASKET = None # This is a default value for BASKET until we get another value from the server.
		colors = ("green", )

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

		thread = threading.Thread(target=Client, daemon=True, args=(referee_ip, referee_port, recv_queue))
		thread.start()

		print(threading.active_count(), " are alive")
		print(threading.enumerate())

		while True:
			# Check whether new info from referee is available
			try:
				referee_data = recv_queue.get(block=False)
				#print(referee_data)
			except queue.Empty:
				pass

			if referee_data != None:
				if robot_name in referee_data["targets"]:
					if referee_data["signal"] == "start":
						STATE = State.FIND_BALL
						BASKET = referee_data["baskets"][referee_data["targets"].index(robot_name)]
						colors = ("green", BASKET)
						cap.update_targets(colors)
					elif referee_data["signal"] == "stop":
						STATE = State.STOP
				referee_data = None

			if STATE != State.STOP and STATE != State.QUIT:
				if cap.has_new_frames:
					# Read capture and detector
					frame = cap.get_color()
					cap.has_new_frames = False
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
					if y_base < 100: # too close is bad
						moveControl.backward(40)
						print("Backing up...")
						continue
					elif y_base < 160:
						persistence += 1
						if persistence > 20: # x stable frames
							print("Found ball") # Ball is close, just stop for now
							persistence = 0
							moveControl.stop()
							# STATE = State.QUIT
							STATE = State.ALIGN # uncomment for aligning and throwing (used in a game)
							target_set = False
					else:
						persistence = 0
						# moveControl.move_at_angle(x, y)
						moveControl.chase_ball(x, y)
						pass

				else:
					# change robot viewpoint to find eligible ball
					current_time = time.time()
					if not start_search_timer: # Time out for when to move to base?
						start_time = time.time()
						start_search_timer = True
					elif current_time - start_time > 5: # No ball seen for x seconds
						start_search_timer = False
						target_set = False
						#print("Did not manage to find ball from the current position, moving to base")
						STATE = State.MOVE_TO_BASE # for game
						#STATE = State.QUIT # for finding a ball
					# moveControl.spin_left(7)
					moveControl.spin_based_on_angle()
					#moveControl.stop() # for simply finding a ball and stopping
					pass
			
			elif STATE == State.MOVE_TO_BASE:
				# Use the baskets as localization references, will drive until it arrives at the center (basket = 2.3 m away)
				# Irrespective of the current one being used, drive towards the furthest one, while looking for balls?
				if not target_set:
					cap.update_targets(("green", "magenta", "blue"))
					target_set = True
					cap.depth_active = True
					time.sleep(0.1)

				ball_coords = detector.find_ball()
				if ball_coords != None:
					if frame_count > 100: # x stable frames
						moveControl.stop()
						time.sleep(0.1)
						frame_count = 0
						cap.depth_active = False
						target_set = False
						print("Found ball from base")
						STATE = State.FIND_BALL
					else:
						frame_count += 1
						continue
				else:
					frame_count = 0
					basket_coords_magenta = detector.find_basket("magenta")
					basket_coords_blue = detector.find_basket("blue")
					if basket_coords_magenta != None:
						x, y = basket_coords_magenta
						distance = cap.get_depth_from_point(x, y)
						if distance > 2:
							moveControl.move_at_angle(x, y)
						else:
							moveControl.spin_left(6) # Too close, search for the basket that's further away
					elif basket_coords_blue != None:
						x, y = basket_coords_blue
						distance = cap.get_depth_from_point(x, y)
						if distance > 2:
							moveControl.move_at_angle(x, y)
						else:
							moveControl.spin_left(6)
					else:
						moveControl.spin_left(6) # No baskets seen, try to find one
						pass

			elif STATE == State.ALIGN:
				if not target_set:
					cap.update_targets(("green", BASKET)) # pick basket
					cap.depth_active = True
					target_set = True
					time.sleep(0.1) # Depth activation
				# Start aligning the ball with the basket	
				basket_coords = detector.find_basket(BASKET)
				ball_coords = detector.find_ball()
				if basket_coords and ball_coords:
					detector.draw_point(frame, basket_coords, text="basket")
					detector.draw_point(frame, ball_coords, text="ball")
					# Perform aligning
					basket_distance = cap.get_depth_from_point(basket_coords[0], basket_coords[1])

					if moveControl.center_ball(ball_coords):
						aligned = moveControl.align_for_throw(ball_coords, basket_coords, basket_distance)
					else: pass

					if aligned:
						STATE = State.THROW
						aligned = False
				else:
					# change robot viewpoint to find ball
					moveControl.rotate_based_on_angle(30)
					current_time = time.time()
					if not align_timer:
						start_time = time.time()
						align_timer = True
					elif current_time - start_time < 8:
						pass
					else:
						print("Alignment timed out")
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
					time_throw = time.time()
					if not start_throw_timer:
						time_throw_start = time.time()
						start_throw_timer = True
					elif time_throw - time_throw_start < 2.5: # Stop the throw after n seconds (timeout)
						moveControl.servo_speed = throw_speed
						moveControl.forward(8) # Need to set it so that the robot adjusts while approaching, now will most prob miss
						# Experimental controlled approach, this too hard, kissy
						# moveControl.aim_and_throw(ball_coords, basket_coords)
					else:
						print("Used throw speed was", throw_speed)
						print("finito throwito")
						moveControl.servo_speed = 0
						start_throw_timer = False
						cap.depth_active = False
						STATE = State.FIND_BALL

			elif STATE == State.STOP:
				moveControl.stop()
				continue

			elif STATE == State.QUIT:
				print('Closing program')
				moveControl.serial_link.stopThread = True # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				break

			# uncomment if your laptop is not running on a potato xd
			#cv2.imshow("View", frame)
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


if __name__ == "__main__":
	main()
