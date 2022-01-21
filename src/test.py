from client import Client
import time
from threading import Thread
import queue

#just "Shaq" for now
robot_name = "001TRT"
referee_ip = "192.168.3.98"
#referee_ip = "localhost"
referee_port = "8765"
referee_data = None
recv_queue = queue.Queue()

thread = Thread(target=Client, args=(referee_ip, referee_port, recv_queue))
thread.start()
while True:
	#print("a")
	time.sleep(0.5)
	#try:
		#received_data = recv_queue.get(block=False)
		#print(received_data)
	#except queue.Empty:
		#pass
# Check whether new info from referee is available
	try:
		referee_data = recv_queue.get(block=False)
		print(referee_data)
	except queue.Empty:
		pass

	if referee_data != None:
		if robot_name in referee_data["targets"]:
			if referee_data["signal"] == "start":
				print("FIND_BALL")
				print(referee_data["baskets"][referee_data["targets"].index(robot_name)])
			elif referee_data["signal"] == "stop":
				print("STOP")
		#else:
			#print(referee_data["signal"])
		referee_data = None
