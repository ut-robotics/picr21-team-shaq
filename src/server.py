import asyncio
import websockets
import config

#ipaddr = "localhost"
ipaddr = "192.168.3.11"
portnum = 8765

async def hello(websocket):
	try:
		comm = input("type 'start' or 'stop' to send: ")
		if comm == "start":
			await websocket.send(str(config.load("referee_start")))
			print("sent start signal")
		elif comm == "stop":
			await websocket.send(str(config.load("referee_stop")))
			print("sent stop signal")

		#received = await websocket.recv()
		#print(f"<<< {received}")

	except websockets.ConnectionClosedOK:
		await websocket.close()

async def main():
	async with websockets.serve(hello, ipaddr, portnum):
		await asyncio.Future()  # run forever

if __name__ == "__main__":
	asyncio.run(main())
