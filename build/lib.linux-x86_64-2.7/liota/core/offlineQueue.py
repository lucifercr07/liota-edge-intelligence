import logging
from collections import deque
import threading

log = logging.getLogger(__name__)

class offlineQueue:
	def __init__(self, size, drop_oldest, drop_newest):
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
		
	def append(self, data):
		if (self.size<0):	#for infinite length deque
			self.d.append(data)
		elif (self.size>0 and self.drop_oldest==1): #for deque with drop_oldest=1
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(self.d[0]))
			self.d.append(data)
		else:									#for deque with drop_newest=1
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(self.d.pop()))
				self.d.append(data)
			else:
				self.d.append(data)

	def _drain(self):
		while self.d:
			print "Data drain: ",self.d.pop()
			if self.d:
				print "Data drain: ",self.d.popleft()

	def start_drain(self):
		queueDrain = threading.Thread(target=self._drain)
		queueDrain.daemon = True
		queueDrain.start()
		queueDrain.join()

	def show(self):
		print self.d
