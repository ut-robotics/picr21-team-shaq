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
from line_sampler import LineSampler
from Movement import Movement
from thrower_calc import Thrower
from manual_teleop import ManualTeleop
from client import Client
import queue

class State(Enum):
	FIND_BALL = "FIND_BALL"
	ALIGN = "ALIGN"
	THROW = "THROW"
	MOVE_TO_BASE = "MOVE_TO_BASE"
	STOP = "STOP"
	QUIT = "QUIT"

def main():
	# STATE = State.FIND_BALL
	# STATE = State.THROW
	#STATE = State.MOVE_TO_BASE
	STATE = State.STOP # During the game this would be the default state until robot receives "start" signal directed to it.
	target_set = False
	start_throw_timer = False
	start_search_timer = False
	align_timer = False
	persistence = 0
	frame_count = 0
	missing_ball_frames = 0
	base_frame_counter = 0
	ball_in_court = True
	ball_centered = False
	aligned = False
	GAME_START = True
	frame = None

	# def quit_alignment():
	# 	target_set = False
	# 	align_timer = False
	# 	STATE = State.FIND_BALL
	# 	missing_ball_frames = 0
	
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
		#BASKET = "magenta"
		colors = ("green", )

		# Initialize capture
		cap = Capture(colors)
		time.sleep(0.2) # ?
		detector = Detector(cap)
		line_sampler = LineSampler()
		thrower = Thrower()
		throw_speed = 0 # Testing purposes
		# --------------------------------------------------
		move_control = Movement() # Includes Communication
		# --------------------------------------------------
		# Manual operation
		# --------------------------------------------------
		#MP = ManualTeleop(move_control, State)
		#print("Controls\n===================================")
		#for key in MP.key_map:
			#print(key + ":\t" + MP.key_map[key] + "\n")
		#print("===================================")
		# --------------------------------------------------

		# Start the threads
		cap.start_thread()
		# Throw measurements:
		# cap.depth_active = True
		# cap.update_targets((BASKET,))

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
						STATE = State.MOVE_TO_BASE
						BASKET = referee_data["baskets"][referee_data["targets"].index(robot_name)]
						colors = ("green", BASKET)
						cap.update_targets(colors)
					elif referee_data["signal"] == "stop":
						STATE = State.STOP
				referee_data = None

			# if STATE != State.STOP and STATE != State.QUIT:
			# 	if cap.has_new_frames:
			# 		# Read capture and detector
			# 		frame = cap.get_color()
			# 		cap.has_new_frames = False
			# 		if frame is None:
			# 			continue
			# 	else:
			# 		continue
			
			# Getting a really bad framerate with the "has_new_frames"
			frame = cap.get_color()
			if frame is None:
				continue

			#if MP.state_update:
				#STATE = MP.STATE
				#MP.state_update = False

			if STATE == State.FIND_BALL:
				print("finding ball")
				if not target_set:
					cap.update_targets(("green",))
					target_set = True # Prevent constant updating?
				ball_mask = cap.masks["green"]
				if ball_mask is None: continue
				
				ball_coords = detector.find_ball(view=frame)
				# ---------------------------------------------------------------
				# Check if outside of court, experimental, probably doesn't work
				# ---------------------------------------------------------------
				SEE_BALL = (ball_coords != None)
				if SEE_BALL:
					ball_in_court = line_sampler.check_ball_in_court(frame, ball_coords)
					if not ball_in_court:
						detector.draw_point(frame, ball_coords, text="0_o", clr=(255, 0, 0))
					else:
						detector.draw_point(frame, ball_coords, text="ball")
				# ---------------------------------------------------------------

				if SEE_BALL and ball_in_court: # If there is an eligible ball (duplicate truth for ease of debug)		
					start_search_timer = False
					x, y = ball_coords
					# print(f"x: {x} y: {y}")
					y_base = move_control.HEIGHT - y
					if y_base < 130: # too close is bad
						move_control.backward(30)
						print("Backing up...")
						time.sleep(0.3)
						continue
					if y_base < 250:
						persistence += 1
						if persistence > 10: # x stable frames
							print("Found ball") # Ball is close, just stop for now
							persistence = 0
							move_control.stop()
							# STATE = State.QUIT
							STATE = State.ALIGN # uncomment for aligning and throwing (used in a game)
							target_set = False
					else:
						persistence = 0
						move_control.chase_ball(x, y)
						pass

				else: # either don't see anything or the ball is out of court
					# change robot viewpoint to find eligible ball
					current_time = time.time()
					if not start_search_timer: # Time out for when to move to base?
						start_time = time.time()
						start_search_timer = True
					elif current_time - start_time > 5: # No ball seen for x seconds
						start_search_timer = False
						target_set = False
						print("Did not manage to find ball from the current position, moving to base")
						STATE = State.MOVE_TO_BASE # for game
					# move_control.spin_left(8)
					move_control.spin_based_on_angle()
					pass
			
			elif STATE == State.MOVE_TO_BASE:
				# Use the baskets as localization references, will drive until it arrives at the center (basket = 2.3 m away)
				# Irrespective of the current one being used, drive towards the furthest one, while looking for balls?
				# At the beginning of the game will drive towards the opposing basket to get to the balls that the robot can actually score
				if not target_set:
					cap.update_targets(("green", "magenta", "blue"))
					target_set = True
					cap.depth_active = True
					time.sleep(0.1)
				
				ball_coords = detector.find_ball()
				if ball_coords != None and not GAME_START:
					if frame_count > 200: # x stable frames
						move_control.stop()
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
							
					if basket_coords_magenta != None or basket_coords_blue != None:
						x, y = basket_coords_magenta if basket_coords_magenta != None else basket_coords_blue
						distance = cap.get_depth_from_point(x, y)
						if distance < 2.3 and GAME_START:
							GAME_START = False
							continue
						elif distance > 2:
							move_control.move_at_angle(x, y)
						else:
							move_control.spin_left(10) # Too close, search for the basket that's further away
					else:
						move_control.spin_left(10) # No baskets seen, try to find one
						pass

			elif STATE == State.ALIGN:
				if not target_set:
					# cap.depth_active = True
					# time.sleep(0.1) # Depth activation
					cap.update_targets(("green", BASKET)) # pick basket
					target_set = True
				# Start aligning the ball with the basket	
				basket_coords = detector.find_basket(BASKET)
				ball_coords = detector.find_ball()
				# Implement something so it goes back to finding the ball if the ball is not seen anymore?
				if basket_coords and ball_coords:
					detector.draw_point(frame, basket_coords, text="basket")
					detector.draw_point(frame, ball_coords, text="ball")
					# Perform aligning
					# basket_distance = cap.get_depth_from_point(basket_coords[0], basket_coords[1])
					y_base = move_control.HEIGHT - ball_coords[1]
					print(y_base)
					if y_base < 100: 
						move_control.backward(20)
						time.sleep(0.3)
						continue
					elif y_base > 270:
						target_set = False
						align_timer = False
						STATE = State.FIND_BALL
						missing_ball_frames = 0 # Too far out now
						print("Lost the ball")
					if move_control.center_ball(ball_coords):
						aligned = move_control.align_for_throw(ball_coords, basket_coords,)# basket_distance)
					else: pass

					if aligned:
						cap.depth_active = True
						STATE = State.THROW
						aligned = False
						missing_ball_frames = 0
						align_timer = 0
						time.sleep(0.1)

				elif ball_coords == None:
					missing_ball_frames += 1
					if missing_ball_frames > 10:
						print("Lost the ball")
						target_set = False
						align_timer = False
						STATE = State.FIND_BALL
						missing_ball_frames = 0
				else:
					# change robot viewpoint to find the basket
					move_control.rotate_based_on_angle(30) # 30 is decent
					current_time = time.time()
					if not align_timer:
						start_time = time.time()
						align_timer = True
					elif current_time - start_time < 8:
						pass
					else:
						print("Alignment timed out")
						target_set = False
						align_timer = False
						STATE = State.FIND_BALL
						missing_ball_frames = 0

			elif STATE == State.THROW:
				# -----------------------------------------
				# For manual interpolation measurements
				# -----------------------------------------		
				# basket_coords = detector.find_basket(BASKET)
				# if basket_coords != None:
				# 	detector.draw_point(frame, basket_coords, text="basket")
				# 	x, y = basket_coords
				# 	basket_distance = cap.get_depth_from_point(x, y)
				# 	print(basket_distance)
				# 	move_control.servo_speed = throw_speed
				# 	move_control.sendSpeed([0, 0, 0])

				# -----------------------------------------
				basket_coords = detector.find_basket(BASKET)
				ball_coords = detector.find_basket("green")

				if basket_coords == None:
					# move_control.spin_based_on_angle()
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
						move_control.servo_speed = throw_speed
						move_control.forward(9) # Need to set it so that the robot adjusts while approaching, now will most prob miss
						# Experimental controlled approach, this too hard, kissy
						# move_control.aim_and_throw(ball_coords, basket_coords)
					else:
						print("Used throw speed was", throw_speed)
						print("finito throwito")
						move_control.servo_speed = 0
						start_throw_timer = False
						cap.depth_active = False
						STATE = State.FIND_BALL

			elif STATE == State.STOP:
				move_control.stop()
				continue

			elif STATE == State.QUIT:
				print('Closing program')
				move_control.serial_link.stopThread = True # QUIT
				cap.running = False
				cv2.destroyAllWindows()
				break

			# uncomment if your laptop is not running on a potato xd
			# cv2.circle(frame, (424, 280), 10, (0, 255, 0), 2)
			#cv2.putText(frame, str(STATE), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
			#cv2.imshow("View", frame)
			#cv2.imshow("Balls", ball_mask)
			#MP.key_control()
			# k = cv2.waitKey(1) & 0xFF
			# if k == ord("q"):
			# 	STATE = State.QUIT
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
