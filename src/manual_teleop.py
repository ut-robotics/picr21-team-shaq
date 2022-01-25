import cv2
import math
import time

import comm

class ManualTeleop:

	directions = {
		"forward": lambda S : [S, -S, 0],
		"backward": lambda S : [-S, S, 0],
		"right": lambda S : [0, 0, -S],
		"left": lambda S : [0, 0, S],
		"spin_left": lambda S : [S, 0, S],
		"spin_right": lambda S : [0, -S, -S],
		"stop": lambda S : [0, 0, 0],
	}

	key_map = {
		"c": "stop",
		"w": "forward",
		"s": "backward",
		"a": "left",
		"d": "right",
		"z": "spin_left",
		"x": "spin_right",
		"f": "decrease speed",
		"g": "increase speed",
		"e": "stop servo",
		"r": "resume servo",
		"t": "decrease servo speed",
		"y": "increase servo speed",
	}

	def __init__(self, moveControl, State):
		self.serial_link = moveControl.serial_link
		self.state_update = False
		self.D = "stop"

		self.speed = 15
		self.servo_speed = 0
		self.current_servo_speed = 400
		self.last_key_press = None
		self.State = State

	def sendSpeed(self, motors, printing=False):
		# Add servo speed
		motors.append(self.servo_speed)
		# Pass the list to communication module
		self.serial_link.incoming_speeds = motors
		if printing:
			print("Sent ", str(motors))

	"""? Calculate the angle towards which robot should drive to get to the ball using the shortest path ?"""


	""" Calculate what should be the individual wheel's velocity based on which angle the robot wants to move on """
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

	def omniMovement(self):
		cv2.namedWindow("Holonomic mode")
		print("c = stop\n i = 45deg\n u = 135deg\n j = -45deg\n k = -135deg \nWASself.D for NSEW")
		while True:
			#degrees = input("self.Direction (degrees): ")
			#self.sendSpeed(self.omni_components(10, int(degrees)), printing=True)

			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				self.serial_link.state = 2 # QUIT
				break
			# self.Driving omni, 8 angles example
			elif key == ord('c'):
				self.sendSpeed([0, 0, 0])
			elif key == ord('u'):
				# 135 degrees
				self.sendSpeed(self.omni_components(10, 135), printing=True)
			elif key == ord('i'):
				# 45 degrees
				self.sendSpeed(self.omni_components(10, 45), printing=True)
			elif key == ord('k'):
				# -45 degrees
				self.sendSpeed(self.omni_components(10, -45), printing=True)
			elif key == ord('j'):
				# -135 degrees
				self.sendSpeed(self.omni_components(10, -135), printing=True)
			elif key == ord('w'):
				# 90 degrees
				self.sendSpeed(self.omni_components(10, 90), printing=True)
			elif key == ord('a'):
				# 180 degrees
				self.sendSpeed(self.omni_components(10, 180), printing=True)
			elif key == ord('s'):
				# 270 degrees
				self.sendSpeed(self.omni_components(10, 270), printing=True)
			elif key == ord('d'):
				# 0 degrees
				self.sendSpeed(self.omni_components(10, 0), printing=True)
			time.sleep(0.1)
			print(self.serial_link.feedback)
			

	def main(self):
		return
		# while True:
		# 	self.key_control()

	def key_control(self):
		key = cv2.waitKey(1) & 0xFF
		# self.Driving basic
		if key == ord('a'):
			self.D = "left"
		elif key == ord('d'):
			self.D = "right"
		elif key == ord('w'):
			self.D = "forward"
		elif key == ord('s'):
			self.D = "backward"
		elif key == ord('z'):
			self.D = "spin_left"
		elif key == ord('x'):
			self.D = "spin_right"
		elif key == ord('c'):
			self.D = "stop"

		# Setting the speed
		elif key == ord('g'):
			self.speed += 5
			print(f"Speed = {self.speed}")
		elif key == ord('f'):
			self.speed -= 5
			print(f"Speed = {self.speed}")

		# Controlling the thrower
		elif key == ord('e'):
			self.servo_speed = 0 # Stop
		elif key == ord('r'):
			self.servo_speed = self.current_servo_speed	# Resume / Start
		elif key == ord('y'):
			self.servo_speed += 200
			self.current_servo_speed += 200
			print(f"Servo speed = {self.current_servo_speed}")
		elif key == ord('t'):
			self.servo_speed -= 200
			self.current_servo_speed -= 200
			print(f"Servo speed = {self.current_servo_speed}")
		elif key ==ord('i'):
			custom_speed = input("Enter test servo speed: ")
			self.servo_speed = custom_speed
			self.current_servo_speed = custom_speed

		# setting the game state
		elif key == ord('1'):
			self.STATE = self.State.STOP
			self.state_update = True
		elif key == ord('2'):
			self.STATE = self.State.FIND_BALL
			self.state_update = True
		elif key == ord('q'):
			self.STATE = self.State.QUIT
			self.state_update = True

		if key == self.last_key_press:
			# no new input,
			pass
		else:
			self.last_key_press = key
			self.sendSpeed(self.directions[self.D](self.speed), printing=False)
			print(f"Direction: {self.D}, Speed: {self.speed}, Thrower speed: {self.current_servo_speed}")


if __name__ == "__main__":
	MP = ManualTeleop()
	MP.main()
	# MP.omniMovement()
