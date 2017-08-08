import unittest
from liota.core.offline_database import offline_database
from liota.dcc_comms.socket_comms import SocketDccComms

comms = SocketDccComms(ip="92.246.246.188",port=8080)

class Testoffline_database(unittest.TestCase):
	
	def test_offline_database_fail_without_valid_table_name(self):
		#Fails if no argument passed
		with self.assertRaises(Exception):
			offline_db = offline_database()
			assertNotIsInstance(offline_db, offline_database)
		
		#Fails if not valid table_name and comms passed
		with self.assertRaises(Exception):
			offline_db = offline_database(table_name=1, comms=None)
			assertNotIsInstance(offline_db, offline_database)

	def test_offline_database_takes_valid_table_name(self):
		
		offline_db = offline_database(size="asd", comms=comms)
		assert isinstance(offline_db, offline_database)

	def test_offline_database_fails_without_valid_draining_frequency(self):
		#Fails if draining_frequency is not float or int
		with self.assertRaises(Exception):
			offline_db = offline_database(size=size, comms=comms, drop_oldest=True, draining_frequency="asd")
			assertNotIsInstance(offline_db, offline_database)

	def test_offline_database_takes_valid_draining_frequency(self):
		offline_db = offline_database(table_name="asd", comms=comms, draining_frequency=1)
		assert isinstance(offline_db, offline_database)

	def test_offline_database_fails_if_draining_frequency_negative(self):
		#Fails if draining_frequency is negative
		with self.assertRaises(Exception):
			offline_db = offline_database(table_name="asd", comms=comms, draining_frequency=-1)
			assertNotIsInstance(offline_db, offline_database)

	def test_offline_database_takes_positive_draining_frequency(self):
		offline_db = offline_database(table_name="asd", comms=comms, draining_frequency=1.0)
		assert isinstance(offline_db, offline_database)

if __name__ == '__main__':
	unittest.main()