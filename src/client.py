import asyncio
import websockets
import ast
from queue import Queue

class Client:

	def __init__(self, ipaddr, portnum, recv_queue):
		#self.received_info = None
		asyncio.run(self.hello(ipaddr, portnum, recv_queue))

	async def hello(self, ipaddr, portnum, recv_queue):

		async for websocket in websockets.connect("ws://" + ipaddr + ":" + portnum):
			try:
				received = await websocket.recv()
				#print(received)
				try:
					received_dict = ast.literal_eval(received)
					#print(received_dict)
					#print(type(received_dict))
					#self.received_info = received_dict
					recv_queue.put(received_dict, block=False)
				except ValueError:
					pass

				#toserver = "just in case"
				#await websocket.send(toserver)

			except websockets.ConnectionClosed:
				continue

if __name__ == "__main__":

	recv_queue = Queue()

	#uri = "ws://localhost:8765"
	#uri = "ws://192.168.3.98:8765"

	socketinfo_str = input("enter socket address and port: ")
	try:
		socketinfo = socketinfo_str.split(':')
		Client(socketinfo[0], socketinfo[1], recv_queue)
	except IndexError:
		print("info was entered incorrectly")
