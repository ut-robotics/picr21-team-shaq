import cv2
import math
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
		 
		self.speed = 5
		self.servo_speed = 100
		self.move_angle = 0

	def sendSpeed(self, motors, printing=False):
		# Add servo speed
		motors.append(self.servo_speed)
		# Pass the list to communication module
		self.serial_link.incoming_speeds = motors
		if printing:
			print("Sent ", str(motors))

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

	def omni_components(self, speed, robotAngle):
		return [
			self.wheelLinearVelocity(speed, 120, robotAngle), # Wheel 1 (right)
			self.wheelLinearVelocity(speed, 240, robotAngle), # Wheel 2 (left)
			self.wheelLinearVelocity(speed, 0, robotAngle),   # Wheel 3 (back)
		]

	def move_at_angle(self, x, y):
		self.move_angle = self.angle_from_coords(x, y) + 10 # add some leeway
		self.speed = self.proportional_speed((x, y))
		omni_components = self.omni_components(self.speed, self.move_angle)
		self.sendSpeed(omni_components)

	def align_for_throw(self, ball_coords, basket_coords):	
		x_basket, y_basket = basket_coords
		x_ball, y_ball = ball_coords

		x_diff = x_basket - x_ball
		#align centers on a 30 pixel window
		if x_diff < 0 and x_diff < -30: # basket on the right of ball, turn left
			self.rotate_left()
			return False
		elif x_diff > 30:
			self.rotate_right()
			return False
		else:
			print("aligned")
			return True

	def proportional_speed(self, ball_coords):
		ball_x, ball_y = ball_coords
		max_speed = 20 # what is it?
		speed = (self.HEIGHT - ball_Y) * max_speed
		return speed

	def speed_from_distance(self, ball_coords, basket_coords):
		# x1, y1 = ball; x2, y2 = basket	
		# The further away the objects are from their desired position, the larget the applied speed should be
		# Get normalized pixel difference (fraction from the frame x and y [-1;1]) and multiply it by the max speed
		ball_x, ball_y = ball_coords
		basket_x, basket_y = basket_coords
		# Create a function that calculates speed based on the distance (y, x coordinates, maybe incorporate depth image?)
		# a.k.a "proportional driving"
		# MAX_SPEED = "?"
		# side_speed = (ball_x - basket_x)/self.WIDTH * max_speed
		# forward_speed = (ball_y - self.y_center)/self.HEIGHT * max_speed
		# rotation = (ball_x - self.x_center)/self.WIDTH * max_speed
		# move_speed = math.sqrt(math.pow(side_speed, 2) + math.pow(forward_speed, 2))
		return

	def spin_based_on_angle(self):
		# last angle used when approaching the ball
		if self.move_angle > 90:
			self.spin_left(self.speed)
		else:
			self.spin_right(self.speed)

	def spin_left(self, S):
		self.sendSpeed([S, S, S])

	def spin_right(self, S):
		self.sendSpeed([-S, -S, -S])

	def rotate_left(self, S):
		self.sendSpeed([-S, 0, -S])
	
	def rotate_right(self, S):
		self.sendSpeed([0, S, S])

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
	
