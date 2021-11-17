import serial
import struct
import threading
import time

import cv2

#state variable describes current state:
#	0 - stop (speed [0,0,0,0] w/ thread running)
#	1 - set speeds
#	2 - quit (put speeds [0,0,0,0] and quit the thread)

class Communication:

	STOP = 0
	SET_SPEEDS = 1
	QUIT = 2

	def __init__(self):
		self.state = self.STOP
		self.incoming_speeds = [0, 0, 0, 0]
		self.ser = serial.Serial('/dev/ttyACM0', timeout=2, write_timeout=2)
		mainboard_thread = threading.Thread(target=self.communication, args=())
		mainboard_thread.start()

	def communication(self):
		while True:
			if self.ser.in_waiting > 0:
				inputbuff = self.ser.read(8)

			if state == self.STOP:
				self.ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))

			elif state == self.SET_SPEEDS:
				m1, m2, m3, serv = self.incoming_speeds
				self.ser.write(struct.pack('<hhhHBH', m1, m2, m3, serv, 0, 0xAAAA))

			elif state == self.QUIT:
				print('Stopping the program')
				self.ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))
				self.ser.read(8)
				self.ser.close()
				break


	def manualInput(self):

		while True:
			incommand = input('Send command: ')
			if incommand == 'quit':
				self.state = self.QUIT
				time.sleep(1)
				break
			elif incommand == 'stop':
				self.state = self.STOP
				continue
			incom_list = incommand.split(',')
			if len(incom_list) == 4:
				try:
					for i in range(len(incom_list)):
						incom_list[i] = int(incom_list[i])
					self.state = self.SET_SPEEDS
					self.incoming_speeds = incom_list
				except:
					print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
			else:
				print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')


if __name__ == "__main__":
	comm = Communication()
	comm.manualInput()





	# whatever = {
	# 	"forward": [1, -1, 0, 0],
	# 	"backward": [1, -1, 0, 0],
	# 	"right": [0, 0, -1, 0],
	# 	"left": [0, 0, 1, 0],
	# 	"alright": [],
	# 	"spin_left": [1, 0, 1],
	# 	"spin_right": [0, -1, -1],
	# }

	# def drive(direction):
	# 	if direction == "forward":
	# 		incoming_speeds == [speed, -speed, 0, 0]
	# 	else if direction == "backward":
	# 		incoming_speeds = [speed, -speed, 0, 0]
	# 	else if direction  == "right":
	# 		incoming_speeds = [0, -speed, 0, 0]
	# 	else if direction == "left":
	# 		incoming_speeds = [0, 0, speed, 0]
	# 	else if direction == "spin_right":
	# 		incoming_speeds = [0, -speed, -speed, 0]
	# 	else if direction == "spin_left":
	# 		incoming_speeds = [speed, 0, speed, 0]
	# 	else if direction == "stop":
	# 		incoming_speeds = [0, 0, 0, 0]


	# def init_drive():
	# 	keyboard.on_press_key("w", lambda _:drive("forward"))
	# 	keyboard.on_press_key("s", lambda _:drive("backward"))
	# 	keyboard.on_press_key("a", lambda _:drive("left"))
	# 	keyboard.on_press_key("d", lambda _:drive("right"))
	# 	keyboard.on_press_key("x", lambda _:drive("stop"))
		
	# mode = "Manual"
	# init_drive()