import sys
import pyrealsense2 as rs
from threading import Thread
import numpy as np
import cv2
import time
# from copy import copy
#------------
if __name__.startswith("src."):
	from src import config
else:
	import Frame
	import config


"""
Frame retrieval from the camera and setting the config for realsense is done here
"""


class Capture:
	def __init__(self, Processor):
		presets = config.load("cam")
		FPS = presets["fps"]

		self.realsense = False
		if self.check_devices():
			self.realsense = True
			# Create a context object. This object owns the handles to all connected realsense devices
			self.pipe = rs.pipeline()
			# Configure streams
			self.config = rs.config()
			self.config.enable_stream(rs.stream.color, 840, 480, rs.format.bgr8, FPS) # https://bit.ly/3oq9IPf
			self.config.enable_stream(rs.stream.depth, 840, 480, rs.format.z16, FPS)
			# Start streaming
			self.pipe.start(self.config)
			#self.profile = self.pipe.start(self.config)
		self.running = True
		self.color_image = None
		self.depth_image = None
		self.pf = None
		self.Processor = Processor

	def capture_thread(self):
		previous_time = 0 
		while self.running:
			start_time = time.time()
			framerate = str(int(1/(start_time - previous_time)))
			previous_time = start_time
			#-------------------------------------#
			frames = self.pipe.wait_for_frames()
			depth_frame = frames.get_depth_frame()
			color_frame = frames.get_color_frame()
			if not depth_frame or not color_frame:
				continue

			# Convert images to numpy arrays
			self.depth_image = np.asanyarray(depth_frame.get_data())
			self.color_image = np.asanyarray(color_frame.get_data())
			#-------------------------------------#
			self.pf = self.Processor.pre_process(self.color_image) # Benchmarked at 0.003
			cv2.putText(self.color_image, f"FPS: {framerate}", (500, 440), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

			if __name__ == "__main__":
				cv2.imshow("RealSense", self.color_image)
				cv2.imshow("RealSense depth", self.depth_image)
				cv2.imshow("Processed frame", self.pf)
				k = cv2.waitKey(1) & 0xFF
				if k == ord("q"):
					print('Closing program')
					self.stop()
					cv2.destroyAllWindows()

	def captureThread(self):
		self.cap = cv2.VideoCapture(0)
		while self.running:
			_, frame = self.cap.read() #(480, 640)
			self.color_image = frame
			self.pf = self.Processor.pre_process(frame)

			if __name__ == "__main__":
				cv2.imshow("Capture", self.color_image)
				cv2.imshow("Processed frame", self.pf)
				k = cv2.waitKey(1) & 0xFF
				if k == ord("q"):
					print('Closing program')
					self.stop()
					cv2.destroyAllWindows()

	def check_devices(self):
		ctx = rs.context()
		devices = ctx.query_devices()
		return len(devices)
	
	def get_pf(self):
		return self.pf
	def get_color(self):
		return self.color_image
	def get_depth(self):
		return self.depth_image

	def start_thread(self):
		Thread(name="Capture", target=self.capture_thread).start()
	def startThread(self):
		Thread(name="Capture", target=self.captureThread).start()

	def stop(self):
		self.running = False
		if self.realsense:
			self.pipe.stop()
		else:
			self.cap.release()


if __name__ == "__main__":
	cap = Capture(Frame.Processor())
	cap.startThread()
	#cap.start_thread()
