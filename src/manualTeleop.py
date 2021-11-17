import cv2
from comm import Communication

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
		"e": "stop servoer",
		"r": "resume servoer",
		"t": "decrease servoer speed",
		"y": "increase servoer speed",
	}

	def __init__(self):
		self.serial_link = Communication()
		self.speed = 0
		self.servo_speed = 0

	def sendSpeed(self, motors):
		# Add servo speed
		full_struct = motors.append(self.servo_speed)
		# Pass the list to communication module
		self.serial_link.incoming_speeds = full_struct

	def main(self):
		cv2.namedWindow("Movement")

		while True:
			key = cv2.waitKey(0) & 0xFF
			if key == ord('q'):
				break
			# Driving
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
			elif key == ord('t'):
				self.servo_speed += 50
			elif key == ord('r'):
				self.servo_speed -= 50

			self.sendSpeed(self.directions[D](speed))


if __name__ == "__main__":
	ManualTeleop.main()
