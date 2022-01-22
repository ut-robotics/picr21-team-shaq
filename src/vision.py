import sys
import pyrealsense2 as rs
from threading import Thread
import numpy as np
import cv2
import time
# from copy import copy

#------------
if __name__.startswith("src."):
	from src import config, Frame
else:
	import config, Frame


"""
1.0
Frame retrieval from the camera and setting the config for realsense is done here

1.1
The frame processing now also rests here, to make everyhting more synced up
"""


class Capture:
	def __init__(self, clrs):
		#----------------------------
        # Load Camera Config
        #----------------------------
		presets = config.load("cam")
		FPS = presets["fps"]
		self.WIDTH = presets["width"]
		self.HEIGHT = presets["height"]
		
		# Load the threshold values for all the colors from config:
		self.colorDict = config.load("colors")
		self.update_targets(clrs)
		# Output, can be read by other modules:
		self.masks = { clr: None for clr in self.colorDict }

		if self.check_devices():
			# Create a context object. This object owns the handles to all connected realsense devices
			self.pipe = rs.pipeline()
			# Configure streams
			self.config = rs.config()
			# If I don't enable the depth stream first, frames don't arrive /shrug
			self.config.enable_stream(rs.stream.depth, self.WIDTH, self.HEIGHT, rs.format.z16, FPS)
			self.config.enable_stream(rs.stream.color, self.WIDTH, self.HEIGHT, rs.format.bgr8, FPS) # https://bit.ly/3oq9IPf

			# Depth config
			# ---------------------------------------------------------
			self.profile = self.pipe.start(self.config)
			# ---------------------------------------------------------
			depth_sensor = self.profile.get_device().first_depth_sensor()
			self.depth_scale = depth_sensor.get_depth_scale()
			self.align = rs.align(rs.stream.color)
			# ---------------------------------------------------------
			# More settings, does this create a reference? No need to pass it anywhere?
			# ---------------------------------------------------------
			self.color_sensor = self.profile.get_device().first_color_sensor()
			self.color_sensor.set_option(rs.option.enable_auto_exposure, False)
			self.color_sensor.set_option(rs.option.enable_auto_white_balance, False)
			self.color_sensor.set_option(rs.option.white_balance, 3500)
			self.color_sensor.set_option(rs.option.exposure, 50)

		else:
			print("Did not find the camera")
			quit()

		self.running = True
		self.depth_active = False

		self.color_image = None
		self.depth_image = None

		self.depth_frame = None
		self.color_frame = None
		#self.pf = None

		self.has_new_frames = False

	def update_targets(self, clrs):
        # Create Processor objects from active input colors
		self.active_processors = { c: Frame.Processor(self.colorDict[c]) for c in clrs if c != None}

	def capture_thread(self):
		previous_time = 0
		posX = self.WIDTH - 140
		posY = self.HEIGHT - 40

		# Will be stopped externally, by setting the "running" bool to False
		while self.running:
			start_time = time.time()
			framerate = str(int(1/(start_time - previous_time)))
			previous_time = start_time
			#-------------------------------------#
			frames = self.pipe.wait_for_frames()

			# Align the depth frame to color frame
			# -----------------------------------------
			if self.depth_active:
				aligned_frames = self.align.process(frames)
				self.depth_frame = aligned_frames.get_depth_frame()
				self.color_frame = aligned_frames.get_color_frame()

				if not self.depth_frame or not self.color_frame:
					continue
			else:
				self.color_frame = frames.get_color_frame()
				if not self.color_frame:
					continue

			# Convert images to numpy arrays
			# ------------------------------------#
			if self.depth_active:
				self.depth_image = np.asanyarray(self.depth_frame.get_data())
			self.color_image = np.asanyarray(self.color_frame.get_data())
			#-------------------------------------#	

			# Process all the colors required, move the masks to output
			for color, processor in self.active_processors.items():
				mask = processor.process_frame(self.color_image) # Benchmarked at 0.0014
				self.masks[color] = mask
				# self.updated = True
			
			# Add FPS metric
			cv2.putText(self.color_image, f"FPS: {framerate}", (posX, posY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

			self.has_new_frames = True

			if __name__ == "__main__":
				self.debug()
		
	def get_depth_from_point(self, x, y):
		z_depth = self.depth_frame.get_distance(x, y)
		return z_depth

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

	def stop(self):
		self.running = False
		self.pipe.stop()

	def debug(self):
		cv2.imshow("RealSense", self.color_image)
		if self.depth_image is not None:
			cv2.imshow("RealSense depth", self.depth_image)
		k = cv2.waitKey(1) & 0xFF
		if k == ord("q"):
			print('Closing program')
			self.stop()
			cv2.destroyAllWindows()

if __name__ == "__main__":
	colors = ("green", "blue")
	cap = Capture(colors)
	cap.start_thread()
