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
		self.response = None
		self.ser = serial.Serial('/dev/ttyACM0', timeout=2, write_timeout=2)
		self.mainboard_thread = threading.Thread(target=self.communication, args=())
		self.mainboard_thread.start()

	def communication(self):
		while True:
			if self.ser.in_waiting > 0:
				self.response = self.ser.read(8)

			if self.state == self.STOP:
				self.ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))

			elif self.state == self.SET_SPEEDS:
				m1, m2, m3, serv = self.incoming_speeds
				self.ser.write(struct.pack('<hhhHBH', m1, m2, m3, serv, 0, 0xAAAA))

			elif self.state == self.QUIT:
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