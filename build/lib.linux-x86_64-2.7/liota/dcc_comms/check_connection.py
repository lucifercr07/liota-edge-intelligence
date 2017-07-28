import urllib2
from liota.dcc_comms.timeout_exceptions import timeoutException

class CheckConnection: #ip can be used as DNS look up time is reduced
	def __init__(self,ip=None,timeout=1):
		self.ip = ip
		self.timeout = timeout

	def checkConn(self):
	    try:
	        urllib2.urlopen('http://216.58.192.142', timeout=self.timeout)
	    except urllib2.URLError as err: 
	        raise timeoutException("Connection timeout. Please Check connection.")

