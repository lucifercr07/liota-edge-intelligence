import logging
from collections import deque
import threading
import time

log = logging.getLogger(__name__)

class offlineQueue:
	def __init__(self, size, drop_oldest, drop_newest, comms, draining_frequency=0):
		try: 
			assert size!=0 and drop_newest!=drop_oldest
		except AssertionError as e:
			raise e

		self.size = size
		self.drop_oldest = drop_oldest
		self.drop_newest = drop_newest
		if (self.size>0 and drop_oldest==1):
			self.d = deque(maxlen=self.size)
		else:
			self.d = deque()
		self.comms = comms
		self.draining_frequency = draining_frequency
		self._offlineQLock = threading.Lock()
		
	def append(self, data):
		if (self.size<0):	#for infinite length deque
			self.d.append(data)
		elif (self.size>0 and self.drop_oldest==1): #for deque with drop_oldest=1
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(self.d[0]))
			self.d.append(data)
		else:									#for deque with drop_newest=1
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(data))
			else:
				self.d.append(data)

	def _drain(self):
		self._offlineQLock.acquire()
		while self.d:
			data = self.d.pop()
			print "Data drain: ",data
			self.comms.send(data)
			if self.d:
				data1 = self.d.popleft()
				print "Data drain: ",data1
				self.comms.send(data1)
			time.sleep(self.draining_frequency)
		self._offlineQLock.release()

	def start_drain(self):
		queueDrain = threading.Thread(target=self._drain)
		queueDrain.daemon = True
		queueDrain.start()
		queueDrain.join()

	def show(self):
		print self.d
