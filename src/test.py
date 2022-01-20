from client import Client
import time
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
		#self.client = self._target(self._args[0], self._args[1])
		#self.last_event = None
		#self.running = False
		self.client = None

	def run(self):
		self.running = True
		try:
			if self._target:
				self.client = self._target(*self._args, **self._kwargs)
		finally:
			del self._target, self._args, self._kwargs
			#self.client = None
		#while self.running:
			#do some websocket stuff
			#self.last_event = "something happened?" # something that you want

	#def event_processed(self):
		#self.last_event = None

thread = WebsocketThread(ipaddr, portnum)
thread.start()

# main loop
while True:
	#if thread.last_event is not None:
		#handle some stuff
		#print(thread.last_event)
		#thread.event_processed()

	# main game logic
	print("a")
	time.sleep(3)
	if thread.client != None:
		if thread.client.received_info != None:
			print(thread.client.received_info)
		else:
			print("no info :(")
	else:
		print("no client :(")

##testthread = threading.Thread(target=Client, args=(ipaddr, portnum))
##testthread.start()
#client_obj = Client(ipaddr, portnum)

#while True:
	#print("a")
	#time.sleep(3)
	##print(testthread.local().received_info)
