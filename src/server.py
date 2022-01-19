import asyncio
import websockets
import config

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
	async with websockets.serve(hello, "localhost", 8765):
		await asyncio.Future()  # run forever

if __name__ == "__main__":
	asyncio.run(main())
