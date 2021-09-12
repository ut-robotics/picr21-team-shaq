import serial
import struct
import threading
import queue
import time

def communication(thread_queue):
	global ser
	while True:
		if ser.in_waiting > 0:
			#likely it's not readline() that is needed here; read() should probably be used here, but I'm currently not sure about what number of bytes to read
			inputbuff = ser.readline()
			received_data = struct.unpack('<hhhH', inputbuff)
			if len(received_data) == 4:
				print('Received from mainboard: ' + received_data[0] + ', ' + received_data[1] + ', ' + received_data[2] + ', ' + received_data[3])
			else:
				print('Something was sent by mainboard, but not what was expected ¯\_(ツ)_/¯')
		try:
			comm = thread_queue.get_nowait()
			if type(comm) is str:
				if comm == 'quit':
					print('Stopping the program')
					ser.write(struct.pack('<hhhHH', 0, 0, 0, 0, 0, 0xAAAA))
					ser.readline()
					ser.close()
					#time.sleep(1)
					break
				elif comm == 'stop':
					ser.write(struct.pack('<hhhHH', 0, 0, 0, 0, 0, 0xAAAA))
			elif type(comm) is list:
				if len(comm) == 4:
					#disable_failsafe = 0 for now
					ser.write(struct.pack('<hhhHH', comm[0], comm[1], comm[2], comm[3], 0, 0xAAAA))
		except queue.Empty:
			pass

#def sendcomm(incom_list):
	#print('writing to mainboard: ' + incom_list[0] + ', ' + incom_list[1] + ', ' + incom_list[2] + ', ' + incom_list[3])
	#ser.write(struct.pack('<hhhHH', incom_list[0], incom_list[1], incom_list[2], incom_list[3], 0xAAAA))

#def receive():
	#pass

#ser = serial.Serial('/dev/ttyUSB0')
ser = serial.Serial('/dev/ttyACM0', timeout=2, write_timeout=2)
#print(ser.name)
thread_queue = queue.Queue()

mainboard_thread = threading.Thread(target=communication, args=(thread_queue, ))
mainboard_thread.start()

while True:
	incommand = input('Send command: ')
	if incommand == 'quit':
		thread_queue.put_nowait(incommand)
		#print('Stopping the program')
		#ser.write(struct.pack('<hhhHH', 0, 0, 0, 0, 0, 0xAAAA))
		#ser.close()
		time.sleep(1)
		break
	elif incommand == 'stop':
		thread_queue.put_nowait(incommand)
	incom_list = incommand.split(',')
	if len(incom_list) == 4:
		#sendcomm(incom_list)
		thread_queue.put_nowait(incom_list)
	else:
		print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
