from client import Client
import time
from threading import Thread
import queue

ipaddr = "192.168.3.98"
#ipaddr = "localhost"
portnum = "8765"

recv_queue = queue.Queue()
thread = Thread(target=Client, args=(ipaddr, portnum, recv_queue))
thread.start()

# main loop
while True:
	print("a")
	time.sleep(0.5)
	try:
		received_data = recv_queue.get(block=False)
		print(received_data)
	except queue.Empty:
		pass
