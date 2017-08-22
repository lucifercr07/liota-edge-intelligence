import os
import threading
import time
from liota.dcc_comms.timeout_exceptions import timeoutException

class checkConnection: 
	def __init__(self, interval=1, hostname = "8.8.8.8"):
		self.interval = interval
		self.hostname = hostname
		self.check = 1
		self.thread = threading.Thread(target=self.run)
		self.thread.daemon = True                           
		self.thread.start()                              

	def run(self):
		while True:
			self.check = self.check_internet()
			#z = self.thread.isAlive()
			time.sleep(self.interval)

	def check_internet(self):
		response = os.system("ping -c 1 " + self.hostname + " > /dev/null 2>&1")
		if response == 0:
			pingstatus = 1
		else:
			pingstatus = 0
		return pingstatus
