import asyncio
import websockets
import ast

class Client:

	def __init__(self, ipaddr, port):
		asyncio.run(hello(ipaddr, port))

async def hello(ipaddr, portnum):

	async for websocket in websockets.connect("ws://" + ipaddr + ":" + portnum):
		try:
			received = await websocket.recv()
			print(received)
			try:
				received_dict = ast.literal_eval(received)
				#print(received_dict)
				#print(type(received_dict))
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

	asyncio.run(hello(socketinfo[0], socketinfo[1]))
