import serial
import struct
import threading
import time

import keyboard

global incoming_speeds, state

#state variable describes current state:
#	0 - stop (speed [0,0,0,0] w/ thread running)
#	1 - set speeds
#	2 - quit (put speeds [0,0,0,0] and quit the thread)
state = 0
incoming_speeds = [0,0,0,0]

#def communication(thread_queue):
def communication():
	global ser, incoming_speeds
	stop_state = False
	while True:
		if ser.in_waiting > 0:
			inputbuff = ser.read(8)
			#speed1, speed2, speed3, thrower_speed = struct.unpack('<hhhH', inputbuff)
			#print('Received from mainboard: ' + str(speed1) + ', ' + str(speed2) + ', ' + str(speed3) + ', ' + str(thrower_speed))
		if state == 0:
			if not stop_state:
				ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))
				stop_state = True
		elif state == 1:
			ser.write(struct.pack('<hhhHBH', incoming_speeds[0], incoming_speeds[1], incoming_speeds[2], incoming_speeds[3], 0, 0xAAAA))
			if stop_state:
				stop_state = False
		elif state == 2:
			print('Stopping the program')
			ser.write(struct.pack('<hhhHBH', 0, 0, 0, 0, 0, 0xAAAA))
			ser.read(8)
			ser.close()
			break

ser = serial.Serial('/dev/ttyACM0', timeout=2, write_timeout=2)

mainboard_thread = threading.Thread(target=communication, args=())
mainboard_thread.start()

def drive(direction):
	if direction == "forward":
		incoming_speeds == [speed, -speed, 0, 0]
	else if direction == "backward":
		incoming_speeds = [speed, -speed, 0, 0]
	else if direction  == "right":
		incoming_speeds = [0, -speed, 0, 0]
	else if direction == "left":
		incoming_speeds = [0, 0, speed, 0]
	else if direction == "spin_right":
		incoming_speeds = [0, -speed, -speed, 0]
	else if direction == "spin_left":
		incoming_speeds = [speed, 0, speed, 0]
	else if direction == "stop":
		incoming_speeds = [0, 0, 0, 0]


def init_drive():
	keyboard.on_press_key("w", lambda _:drive("forward"))
	keyboard.on_press_key("s", lambda _:drive("backward"))
	keyboard.on_press_key("a", lambda _:drive("left"))
	keyboard.on_press_key("d", lambda _:drive("right"))
	keyboard.on_press_key("x", lambda _:drive("stop"))
	# try:  # used try so that if user pressed other than the given key error will not be shown
	# 	if keyboard.is_pressed('q'):  # if key 'q' is pressed 
	# 		print('You Pressed A Key!')
	# 		break  # finishing the loop
	# 	else if keyboard.is_pressed('s'):

	# except:
	# 	break  # if user pressed a key other than the given key the loop will break
	
mode = "Manual"
init_drive()

while True:

	keyboard.wait()
	continue

	incommand = input('Send command: ')
	if incommand == 'quit':
		state = 2
		time.sleep(1)
		break
	elif incommand == 'stop':
		state = 0
		continue
	incom_list = incommand.split(',')
	if len(incom_list) == 4:
		try:
			for i in range(len(incom_list)):
				incom_list[i] = int(incom_list[i])
			state = 1
			incoming_speeds = incom_list
		except:
			print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
	else:
		print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
