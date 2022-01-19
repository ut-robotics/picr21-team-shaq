from client import Client
import time
#import threading
from threading import Thread

ipaddr = "192.168.3.98"
#ipaddr = "localhost"
portnum = "8765"

class WebsocketThread(Thread):
	def __init__(self, ipaddr, portnum):
		super().__init__()
		self._target = Client
		self._args = (ipaddr, portnum)
		#self.client = Client(ipaddr, portnum)
		self.last_event = None
		self.running = False

	def run(self):
		self.running = True
		while self.running:
			# do some websocket stuff
			self.last_event = None # something that you want

	def event_processed(self):
		self.last_event = None

thread = WebsocketThread(ipaddr, portnum)
thread.start()

# main loop
while True:
	if thread.last_event is not None:
		# handle some stuff
		thread.event_processed()

	# main game logic
	print("a")
	time.sleep(3)

##testthread = threading.Thread(target=Client, args=(ipaddr, portnum))
##testthread.start()
#client_obj = Client(ipaddr, portnum)

#while True:
	#print("a")
	#time.sleep(3)
	##print(testthread.local().received_info)
