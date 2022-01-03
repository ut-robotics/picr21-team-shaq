from comm import Communication
import time

commObj = Communication()

while True:

	incommand = input('Send command: ')
	if incommand == 'quit':
		print('Stopping the program')
		commObj.stopThread = True
		time.sleep(1)
		break
	elif incommand == 'stop':
		commObj.incoming_speeds = [0, 0, 0, 0]
		continue
	incom_list = incommand.split(',')
	if len(incom_list) == 4:
		try:
			for i in range(len(incom_list)):
				incom_list[i] = int(incom_list[i])
			commObj.incoming_speeds = incom_list
		except:
			print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
	else:
		print('False input. Input should be in form speed1,speed2,speed3,thrower_speed')
