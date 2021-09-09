import serial
import struct

def sendcomm(incom_list):
	print('writing to mainboard: ' + incom_list[0] + ', ' + incom_list[1] + ', ' + incom_list[2] + ', ' + incom_list[3])
	ser.write(struct.pack('<hhhHH', incom_list[0], incom_list[1], incom_list[2], incom_list[3], 0xAAAA))

def receive():
	pass

#ser = serial.Serial('/dev/ttyUSB0')
ser = serial.Serial('/dev/ttyACM0', timeout=2, write_timeout=2)
#print(ser.name)

while True:
	incommand = input('Send command: ')
	if incommand == 'quit':
		print('Stopping the program')
		ser.write(struct.pack('<hhhHH', 0, 0, 0, 0, 0xAAAA))
		ser.close()
		#time.sleep(1)
		break
	incomm_list = incommand.split(',')
	if len(incom_list) == 4:
		sendcomm(incom_list)
	else:
		print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
