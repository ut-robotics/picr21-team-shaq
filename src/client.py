import asyncio
import websockets
import ast

class Client:

	def __init__(self, ipaddr, portnum):
		self.received_info = None
		asyncio.run(self.hello(ipaddr, portnum))

	async def hello(self, ipaddr, portnum):

		async for websocket in websockets.connect("ws://" + ipaddr + ":" + portnum):
			try:
				received = await websocket.recv()
				#print(received)
				try:
					received_dict = ast.literal_eval(received)
					#print(received_dict)
					#print(type(received_dict))
					self.received_info = received_dict
				except ValueError:
					pass

				#toserver = "just in case"
				#await websocket.send(toserver)

			except websockets.ConnectionClosed:
				continue

if __name__ == "__main__":
	socketinfo_str = input("enter socket address and port: ")
	try:
		socketinfo = socketinfo_str.split(':')
	except IndexError:
		print("info was entered incorrectly")

	#uri = "ws://localhost:8765"
	#uri = "ws://192.168.3.98:8765"

	Client(socketinfo[0], socketinfo[1])
