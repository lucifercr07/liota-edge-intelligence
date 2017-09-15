import unittest
from liota.core.offlineQueue import offlineQueue
from liota.dcc_comms.socket_comms import SocketDccComms

comms = SocketDccComms(ip="92.246.246.188",port=8080)
size = 1

class TestofflineQueue(unittest.TestCase):
	
	def test_offlineQueue_fail_without_valid_size(self):
		#Fails if no argument passed
		with self.assertRaises(Exception):
			offlineQ = offlineQueue()
			assertNotIsInstance(offlineQ, offlineQueue)
		
		#Fails if not valid size and comms passed
		with self.assertRaises(Exception):
			offlineQ = offlineQueue(size="asd", comms=None)
			assertNotIsInstance(offlineQ, offlineQueue)

	def test_offlineQueue_takes_valid_size(self):
		
		offlineQ = offlineQueue(size=size, comms=comms)
		assert isinstance(offlineQ, offlineQueue)

	def test_offlineQueue_fail_with_invalidArg_drop_oldest(self):
		#Fails if bool not passed as drop_oldest
		with self.assertRaises(Exception):
			offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=1)
			assertNotIsInstance(offlineQ, offlineQueue)

	def test_offlineQueue_takes_validArg_drop_oldest(self):
		offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=True)
		assert isinstance(offlineQ, offlineQueue)

	def test_offlineQueue_fails_without_valid_draining_frequency(self):
		#Fails if draining_frequency is not float or int
		with self.assertRaises(Exception):
			offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=True, draining_frequency="asd")
			assertNotIsInstance(offlineQ, offlineQueue)

	def test_offlineQueue_takes_valid_draining_frequency(self):
		offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=True, draining_frequency=1)
		assert isinstance(offlineQ, offlineQueue)

	def test_offlineQueue_fails_if_draining_frequency_negative(self):
		#Fails if draining_frequency is negative
		with self.assertRaises(Exception):
			offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=True, draining_frequency=-1)
			assertNotIsInstance(offlineQ, offlineQueue)

	def test_offlineQueue_takes_positive_draining_frequency(self):
		offlineQ = offlineQueue(size=size, comms=comms, drop_oldest=True, draining_frequency=1.0)
		assert isinstance(offlineQ, offlineQueue)

	def test_offlineQueue_fails_if_size_zero(self):
		#Fails if size is zero
		with self.assertRaises(Exception):
			offlineQ = offlineQueue(size=0, comms=comms, drop_oldest=True, draining_frequency=1)
			assertNotIsInstance(offlineQ, offlineQueue)

	def test_offlineQueue_takes_anyint_except_zero_as_size(self):
		offlineQ = offlineQueue(size=-1, comms=comms, drop_oldest=True, draining_frequency=1.0)
		assert isinstance(offlineQ, offlineQueue)

if __name__ == '__main__':
	unittest.main()