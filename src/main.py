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

		lock = threading.Lock() # not required

		detector.start_thread(cap, lock)
		cap.start_thread()

		print(threading.active_count(), " are alive")
		print(threading.enumerate())
		
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
							#example of how it theoretically should work
							if coords_ball[0] < 270:
								print("turn left")
								set_speeds = [2,0,2,0]
							elif coords_ball[0] > 370:
								print("turn right")
								set_speeds = [0,-2,-2,0]
							if coords_ball[1] < 200:
								print("go forwards")
								set_speeds = [2,-2,0,0]
							elif coords_ball[1] > 280:
								print("go backwards")
								set_speeds = [-2,2,0,0]
						else:
							print("stop")
							#stopping for now, but it probably should just go forwards in the absence of balls
							#set_speeds = [2,-2,0,0]
							set_speeds = [0,0,0,0]
					cv2.imshow(clr.title(), Frames[i])
					cv2.imshow(f"Mask {clr}", masks[clr]) 

			k = cv2.waitKey(1) & 0xFF
			if k == ord("q"):
				print('Closing program')
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
