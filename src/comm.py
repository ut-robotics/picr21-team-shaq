import serial
import struct
import threading
import serial.tools.list_ports as ports
import time

class Communication:

	def __init__(self):
		port_num = None
		for i in range(len(ports.comports())):
			if ports.comports()[i].product == "STM32 Virtual ComPort":
				port_num = i
				break
		if port_num is not None:
			self.incoming_speeds = [0, 0, 0, 0]
			self.response = None
			self.ser = serial.Serial(ports.comports()[port_num].device, timeout=2, write_timeout=2)
			self.stopThread = False
			self.mainboard_thread = threading.Thread(target=self.communication, args=())
			self.mainboard_thread.start()
		else:
			print("No mainboard found!")

	def communication(self):
		while True:

			if self.ser.in_waiting > 0:
				self.response = self.ser.read(8)
				#print(self.response)

			if self.stopThread:
				self.ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))
				self.ser.read(8)
				self.ser.close()
				break

			m1, m2, m3, serv = self.incoming_speeds
			self.ser.write(struct.pack('<hhhHBH', m1, m2, m3, serv, 0, 0xAAAA))
			time.sleep(0.008)
