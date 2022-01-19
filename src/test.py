from client import Client
import time
#import threading

#testthread = threading.Thread(target=Client, args=("192.168.3.98", "8765"))
#testthread.start()
client_obj = Client("192.168.3.98", "8765")

while True:
	print("a")
	time.sleep(3)
	#print(testthread.local().received_info)
