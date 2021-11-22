import cv2
import time
import numpy as np
import threading
from copy import copy
#----------------------------
import config
import Frame
from vision import Capture
from Detection import Detector
from comm import Communication

#variable for setting speeds of motors
set_speeds = [0,0,0,0]

def main():
	try:
		#colors = ("dark_green", "orange")
		colors = ("dark_green",)
		# Initialize capture with a configured Pre-processor 
		cap = Capture(Frame.Processor())
		detector = Detector(colors)
		coords = {}
		# detector.getgreencoords
		# detector.getbluecoords
		# detector.stopColor
		# detector.startColor
		# detector.setColor

		detector.start_thread(cap)
		cap.start_thread()

		print(threading.active_count(), " are alive")
		print(threading.enumerate())

		comm_main = Communication()

		motor_speed = 4
		motor_speed_opposite = -motor_speed

		while True:
			# Read capture and detector
			frame = cap.get_color()
			masks = detector.color_masks

			if frame is not None and len(masks):
				Frames = [copy(frame) for _ in range(len(colors))]
				for i, clr in enumerate(colors):
					coords[clr] = detector.draw_entity(clr, Frames[i]) # Draws on frame and returns draw location
					if clr == "dark_green":
						if coords[clr]:
							coords_ball = coords[clr]
							print("(x,y) coordinates of the ball: " + str(coords_ball))
							if coords_ball[0] < 270:
								print("turn left")
								set_speeds = [motor_speed,0,motor_speed,0]
							elif coords_ball[0] > 370:
								print("turn right")
								set_speeds = [0,motor_speed_opposite,motor_speed_opposite,0]
							else:
								if coords_ball[1] < 200:
									print("go forwards")
									set_speeds = [motor_speed,motor_speed_opposite,0,0]
								elif coords_ball[1] > 280:
									print("go backwards")
									set_speeds = [motor_speed_opposite,motor_speed,0,0]
								else:
									print("stay here")
									set_speeds = [0,0,0,0]
							comm_main.state = 1
							comm_main.incoming_speeds = set_speeds
						else:
							print("go forwards")
							set_speeds = [motor_speed,motor_speed_opposite,0,0]
							comm_main.state = 1
							comm_main.incoming_speeds = set_speeds
							#print("stop")
							#comm_main.state = 0
					# Windows should generally not be created as they're significantly slowing down the execution.
					# Do not delete those lines though, they're useful for testing/debugging.
					#cv2.imshow(clr.title(), Frames[i])
					#cv2.imshow(f"Mask {clr}", masks[clr]) 

			k = cv2.waitKey(1) & 0xFF
			if k == ord("q"):
				print('Closing program')
				comm_main.state = 2
				cap.running = False
				cv2.destroyAllWindows()
				break
			time.sleep(0.05)

	except Exception as e:
		print(e)
		cv2.destroyAllWindows()
		cap.running = False

if __name__ == "__main__":
	main()
