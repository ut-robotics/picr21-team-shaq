import cv2
import math

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import comm

class ManualTeleop:

	directions = {
		"forward": (lambda S : [S, -S, 0]),
		"backward": (lambda S : [S, -S, 0]),
		"right": (lambda S : [0, 0, -S]),
		"left": (lambda S : [0, 0, S]),
		"spin_left": (lambda S : [S, 0, S]),
		"spin_right": (lambda S : [0, -S, -S]),
		"stop": (lambda S : [0, 0, 0]),
	}

	key_map = {
		"w": "forward",
		"s": "backward",
		"a": "left",
		"d": "right",
		"z": "spin_left",
		"x": "spin_right",
		"f": "decrease_speed",
		"g": "increase_speed",
		"e": "stop servo",
		"r": "resume servo",
		"t": "decrease servo speed",
		"y": "increase servo speed",
	}

	def __init__(self):
		self.serial_link = comm.Communication()
		self.speed = 0
		self.servo_speed = 0

	def sendSpeed(self, motors, printing=False):
		# Add servo speed
		full_struct = motors.append(self.servo_speed)
		# Pass the list to communication module
		self.serial_link.incoming_speeds = full_struct
		if printing:
			print(f"Sent {str(full_struct)}")

	"""? Calculate the angle towards which robot should drive to get to the ball using the shortest path ?"""


	""" Calculate what should be the individual wheel's velocity based on which angle the robot wants to move on """
	def wheelLinearVelocity(self, speed, wheelAngle, robotAngle):
		velocity = speed * math.cos(math.radians(robotAngle - wheelAngle))
		return velocity

	def omni_components(self, speed, robotAngle):
		return [
			self.wheelLinearVelocity(speed, 0, robotAngle),
			self.wheelLinearVelocity(speed, 120, robotAngle),
			self.wheelLinearVelocity(speed, 240, robotAngle),
		]

	def omniMovement(self):
		cv2.namedWindow("Movement")
		while True:
			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				self.serial_link.state = 2 # QUIT
				break
			# Driving omni, 4 angles example
			elif key == ord('u'):
				# 135 degrees
				self.sendSpeed(omni_components(10, 135), printing=True)
			elif key == ord('i'):
				# 45 degrees
				self.sendSpeed(omni_components(10, 45), printing=True)
			elif key == ord('k'):
				# -135 degrees
				self.sendSpeed(omni_components(10, -135), printing=True)
			elif key == ord('j'):
				# -45 degrees
				self.sendSpeed(omni_components(10, -45), printing=True)

	def main(self):
		cv2.namedWindow("Movement")
		last_key_press = None
		while True:
			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				self.serial_link.state = 2 # QUIT
				break
			# Driving basic
			elif key == ord('a'):
				D = "left"
			elif key == ord('d'):
				D = "right"
			elif key == ord('w'):
				D = "forward"
			elif key == ord('s'):
				D = "backward"
			elif key == ord('z'):
				D = "spin_left"
			elif key == ord('x'):
				D = "spin_right"
			elif key == ord('c'):
				D = "stop"

			# Setting the speed
			elif key == ord('g'):
				self.speed += 1
			elif key == ord('f'):
				self.speed -= 1

			# Controlling the thrower
			elif key == ord('e'):
				self.servo_speed = 0
			elif key == ord('r'):
				self.servo_speed = 200
			elif key == ord('y'):
				self.servo_speed += 50
			elif key == ord('t'):
				self.servo_speed -= 50

			if key == last_key_press:
				# no new input,
				continue
			else:
				last_key_press = key
				self.sendSpeed(self.directions[D](speed))
				print(f"Direction: {D}, Speed: {self.speed}, Thrower speed: {self.servo_speed}, Omni angle: {angle}")


if __name__ == "__main__":
	ManualTeleop.main()
