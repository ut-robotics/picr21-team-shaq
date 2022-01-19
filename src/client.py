import asyncio
import websockets
import ast

async def hello():

	while True:
		socketinfo_str = input("enter socket address and port: ")
		try:
			socketinfo = socketinfo_str.split(':')
			uri = "ws://" + socketinfo[0] + ":" + socketinfo[1]
			break
		except IndexError:
			print("info was entered incorrectly")
	#uri = "ws://localhost:8765"

	async for websocket in websockets.connect(uri):
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
	asyncio.run(hello())
