# THIS FILE IS USED ONLY FOR DEMOSTRATING THE TASK 2, NOT USED IN GAME LOGIC

from enum import Enum
import cv2
import threading
import traceback
from vision import Capture
from simp_detection import Detector
from Movement import Movement
import time

class State(Enum):
	FIND_BALL = 0
	QUIT = 6

STATE = State.FIND_BALL
target_set = False

try:
	cap = Capture(("green", ))
	time.sleep(0.5)
	detector = Detector(cap)
	moveControl = Movement()
	speed = 7
	xcntr = moveControl.x_center
	ycntr = moveControl.y_center
	allow_range = moveControl.WIDTH * 0.1
	x_left = xcntr - allow_range
	x_right = xcntr + allow_range
	cap.start_thread()

	print(threading.active_count(), " are alive")
	print(threading.enumerate())

	while True:
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
				if x < x_left:
					print("i should turn left")
					moveControl.turn_left(speed)
				elif x > x_right:
					print("i should turn right")
					moveControl.turn_right(speed)
				else:
					if y < ycntr:
						print("i should move forwards")
						moveControl.forward(speed)
					else:
						moveControl.stop()

			else:
				moveControl.stop()

		elif STATE == State.QUIT:
			print('Closing program')
			moveControl.serial_link.stopThread = True
			cap.running = False
			cv2.destroyAllWindows()
			break

		cv2.imshow("View", frame)
		cv2.imshow("Balls", ball_mask)

		k = cv2.waitKey(1) & 0xFF
		if k == ord("q"):
			STATE = State.QUIT

except Exception:
	print(traceback.format_exc())
	cv2.destroyAllWindows()
	cap.running = False
