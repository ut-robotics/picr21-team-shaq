import asyncio
import websockets
import config

#ipaddr = "localhost"
ipaddr = "192.168.3.98"
portnum = 8765

async def hello(websocket):
	try:
		input("press enter to send")
		await websocket.send(str(config.load("referee_test")))
		print("just sent data")

		#received = await websocket.recv()
		#print(f"<<< {received}")

	except websockets.ConnectionClosedOK:
		await websocket.close()

async def main():
	async with websockets.serve(hello, ipaddr, portnum):
		await asyncio.Future()  # run forever

if __name__ == "__main__":
	asyncio.run(main())
