import cv2
import math
import numpy as np
import time
#from simple_pid import PID
import Frame
import config
import comm

class Movement:

	def __init__(self):
		presets = config.load("cam")
		self.HEIGHT = presets["height"]
		self.WIDTH = presets["width"]
		self.x_center = self.WIDTH / 2
		self.y_center = self.HEIGHT / 2
		
		self.serial_link = comm.Communication()

		#self.max_speed = 40 # 40 for regular game probably
		self.max_speed = 10 # 10 for testing purposes so that the robot won't go too fast
		self.speed = 10
		self.spin_speed = 6
		self.rotation_speed = 10
		self.servo_speed = 0
		self.move_angle = 0

		self.align_switch = False

	def sendSpeed(self, motors, printing=False):
		# Add servo speed
		motors.append(self.servo_speed)
		# Pass the list to communication module
		self.serial_link.incoming_speeds = motors
		if printing:
			print("Sent ", str(motors))

	def set_throw_speed(self, speed):
		self.servo_speed = speed
	
	def stop(self):
		self.serial_link.incoming_speeds = [0, 0, 0, 0]

	"""? Calculate the angle towards which robot should drive to get to the ball using the shortest path ?"""
	def angle_from_coords(self, x, y): #(640, 480) x, y
		# Use x center pixel as base
		# Get the difference from center
		x_diff = self.x_center - x
		# Get y distance from camera baseline
		y_base = self.y_center - y

		try:
			angle = 90 + math.degrees(math.atan(x_diff / y_base))
		except ZeroDivisionError:
			angle = 0.01
		return angle

	""" Calculate what should be the individual wheel's speed based on which angle the robot wants to move on """
	def wheelLinearVelocity(self, speed, wheelAngle, robotAngle):
		# Get the according wheel component in the specified radial direction (relative to camera)
		# Use the difference between the target angle and wheel's static angle to get the multiplier
		# e.g. Robot wants to move 0 deg (strafe right),
		#       - back wheel gets full speed (cos(0) = 1),
		#       - right one gets half speed backwards (cos(120) = -0.5),
		#       - left wheel gets half speed backward (cos(240) = -0.5)
		#       In total you get 2x speed right, instead of say moving simply the back wheel
		#       The components on the y axis of the right and left wheel cancel out
		
		velocity = speed * math.cos(math.radians(robotAngle - wheelAngle))
		return int(velocity)

	def omni_components(self, speed, robotAngle, rotation_speed=0):
		return [
			self.wheelLinearVelocity(speed, 120, robotAngle) + rotation_speed, # Wheel 1 (right)
			self.wheelLinearVelocity(speed, 240, robotAngle) + rotation_speed, # Wheel 2 (left)
			self.wheelLinearVelocity(speed, 0, robotAngle) + rotation_speed,   # Wheel 3 (back)
		]
	
	def move_omni(self, speed, robot_angle, rotation_speed):
		omni_components = self.omni_components(speed, robot_angle, rotation_speed)
		self.sendSpeed(omni_components)
    
	def move_omni_xy(self, speed_x, speed_y, rotation_speed=0):
		self.move_angle = math.atan2(speed_y, speed_x)
		speed = int(math.hypot(speed_x, speed_y))
		self.move_omni(speed, self.move_angle, int(rotation_speed))

	def chase_ball(self, x, y):
		speed_x, speed_y, rotation_speed = self.calc_speed(x, y)
		self.move_omni_xy(int(speed_x), int(speed_y), int(rotation_speed))

	def calc_speed(self, x, y):
		speed_y = (abs(y - self.HEIGHT) / self.HEIGHT) * self.max_speed
		# Calculate x_diff, which is proportional to the target distance
		# If ball is on the right, it will be negative, corresponding to the motor directions
		x_diff = (self.x_center - x) / self.x_center
		speed_x =  x_diff * self.max_speed
		speed_rotation = x_diff * self.rotation_speed
		return (speed_x, speed_y, speed_rotation) # careful, floats

	def move_at_angle(self, x, y):
		self.move_angle = self.angle_from_coords(x, y)
		# Adjust for more centered angle, take a wider approach, so ball more centered?
		if self.move_angle < 90:
			self.move_angle - 10
		elif self.move_angle > 90:
			self.move_angle + 10
		speed = self.proportional_speed((x, y))
		omni_components = self.omni_components(speed, self.move_angle)
		self.sendSpeed(omni_components)

	def drive_angle(self, speed, angle, rotation_speed):
		omni_components = self.omni_components(speed, angle)
		self.sendSpeed(omni_components)

	def center_ball(self, ball_coords):
		x_ball, _ = ball_coords
		if x_ball > self.x_center + 10:
			self.drive_angle(5, 10)
			return False
		elif x_ball < self.x_center - 10:
			self.drive_angle(5, 170)
			return False
		else:
			return True

	def align_for_throw(self, ball_coords, basket_coords):	
		x_basket, y_basket = basket_coords
		x_ball, y_ball = ball_coords

		x_diff = x_basket - x_ball
		#align centers on a defined pixel window
		if x_diff > 4: # basket on the right of ball, turn left
			self.rotate_left()
			self.align_switch = False
			return False
		elif x_diff < -4:
			self.align_switch = False
			self.rotate_right()
			return False
		elif not self.align_switch:
			self.stop()
			time.sleep(0.5)
			self.align_switch = True # Check if after stopping still aligned or something
		else:
			print("Ball aligned with basket")
			return True
	
	def attempt_throw(self, ball_coords, basket_coords):
		x_basket, y_basket = basket_coords
		x_ball, y_ball = ball_coords

		x_diff = x_basket - x_ball
		# Simple bang bang approach
		if x_diff > 2: # basket on the right of ball, turn left
			self.rotate_left()
			#self.drive_angle(10, 0)
		elif x_diff < -2:
			self.rotate_right()
			#self.drive_angle(10, 180)
		else:
			self.forward(10)

	def proportional_speed(self, ball_coords):
		ball_x, ball_y = ball_coords
		#max_speed = 40 # what is it?
		max_speed = 10 # for testing purposes
		speed = (abs(ball_y - self.HEIGHT) / self.HEIGHT) * max_speed
		return int(speed)

	def speed_from_distance(self, ball_coords, basket_coords):
		# x1, y1 = ball; x2, y2 = basket	
		# The further away the objects are from their desired position, the larget the applied speed should be
		# Get normalized pixel difference (fraction from the frame x and y [-1;1]) and multiply it by the max speed
		ball_x, ball_y = ball_coords
		basket_x, basket_y = basket_coords
		# Create a function that calculates speed based on the distance (y, x coordinates, maybe incorporate depth image?)
		# a.k.a "proportional driving"
		# MAX_SPEED = 40
		# side_speed = (ball_x - basket_x)/self.WIDTH * max_speed
		# forward_speed = (ball_y - self.y_center)/self.HEIGHT * max_speed
		# rotation = (ball_x - self.x_center)/self.WIDTH * max_speed
		# move_speed = math.sqrt(math.pow(side_speed, 2) + math.pow(forward_speed, 2))
		return

	def spin_based_on_angle(self):
		# last angle used when approaching the ball
		if self.move_angle > 90:
			self.spin_left(self.spin_speed)
		else:
			self.spin_right(self.spin_speed)
	
	def rotate_based_on_angle(self, speed=10):
		# last angle used when approaching the ball
		if self.move_angle > 90:
			self.rotate_left(speed)
		else:
			self.rotate_right(speed)

	def spin_left(self, S):
		self.sendSpeed([S, S, S])

	def spin_right(self, S):
		self.sendSpeed([-S, -S, -S])

	def rotate_left(self, S=10):
		self.sendSpeed([0, 2, -S])
	
	def rotate_right(self, S=10):
		self.sendSpeed([0, -2, S])

	def forward(self, S):
		self.sendSpeed([S, -S, 0])

	def turn_left(self, S):
		self.sendSpeed([S, 0, S])

	def turn_right(self, S):
		self.sendSpeed([0, -S, -S])

	def omniMovement(self):
		cv2.namedWindow("Holonomic mode")
		print("c = stop\n i = 45deg\n u = 135deg\n j = -45deg\n k = -135deg")
		while True:
			degrees = input("Direction (degrees): ")
			self.sendSpeed(self.omni_components(10, int(degrees), printing=True))

			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				self.serial_link.stopThread = True # QUIT
				break
			# Driving omni, 4 angles example
			elif key == ord('c'):
				self.sendSpeed([0, 0, 0])
			elif key == ord('u'):
				# 135 degrees
				self.sendSpeed(self.omni_components(10, 135), printing=True)
			elif key == ord('i'):
				# 45 degrees
				self.sendSpeed(self.omni_components(10, 45), printing=True)
			elif key == ord('k'):
				# -135 degrees
				self.sendSpeed(self.omni_components(10, -135), printing=True)
			elif key == ord('j'):
				# -45 degrees
				self.sendSpeed(self.omni_components(10, -45), printing=True)


if __name__ == "__main__":
	pass
	
