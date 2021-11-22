import cv2
import math
#from simple_pid import PID

import comm

class Movement:

	def __init__(self):
		self.serial_link = comm.Communication()
		self.serial_link.state = 1 # Set speeds

		self.speed = 5
		self.servo_speed = 100

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
		x_center = 320
		y_center = 240
		# Get the difference from center
		x_diff = x_center - x
		# Get y distance from camera baseline
		y_base = 480 - y

		# Ball is close, just stop for now
		if y_base < 50:
			print("<50, stopping")
			self.serial_link_state = 2 # QUIT

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
	
	def move_towards_ball(self, x, y):
		angle = self.angle_from_coords(x, y)
		omni_components = self.omni_components(self.speed, angle)
		self.sendSpeed(omni_components)

	def omniMovement(self):
		cv2.namedWindow("Holonomic mode")
		print("c = stop\n i = 45deg\n u = 135deg\n j = -45deg\n k = -135deg")
		while True:
			degrees = input("Direction (degrees): ")
			self.sendSpeed(self.omni_components(10, int(degrees), printing=True))

			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				self.serial_link.state = 2 # QUIT
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
	return
	
