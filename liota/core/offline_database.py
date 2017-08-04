import sqlite3
import threading
import time

class offline_database:
	def __init__(self, table_name, comms=None, interval=0.0):
		self.table_name = table_name
		self.interval = interval
		self.comms = comms
		self.flag_conn_open = False
		self._create_table()

	def _create_table(self):
		if self.flag_conn_open is False:
			self.conn = sqlite3.connect('storage.db')
			try:
				with self.conn:
					if not self.conn.execute("SELECT name FROM sqlite_master WHERE TYPE='table' AND name= ? ", (self.table_name,)).fetchone():
						self.conn.text_factory = str
						self.flag_conn_open = True
						self.cursor = self.conn.cursor()
						self.cursor.execute("CREATE TABLE "+self.table_name+" (Message TEXT)")
						self.cursor.close()
						del self.cursor
					else:
						self._drain()		
						self._create_table()
			except Exception as e:
				raise e
			finally:
				self.flag_conn_open = False
				self.conn.close()
		#else:    where the data will be stored while connection is open


	def add(self, message):
		try:
			self.conn = sqlite3.connect('storage.db')
			self.flag_conn_open = True
			with self.conn:
				self.cursor = self.conn.cursor()
				self.cursor.execute("INSERT INTO "+self.table_name+" VALUES (?);", (message,))
				self.cursor.close()
				del self.cursor
		except sqlite3.OperationalError as e:
			raise e
		finally:
			self.conn.close()
			self.flag_conn_open = False

	def _drain(self):
		self.conn = sqlite3.connect('storage.db')
		self.flag_conn_open = True
		self.cursor = self.conn.cursor()
		try:
			with self.conn:
				for row in self.cursor.execute("SELECT Message FROM "+self.table_name):
					if self.comms is not None:
						print "Data Drain:",row[0]
						self.comms.send(row[0])
					else:
						print "DATA DRAIN:",row[0]
					time.sleep(self.interval)
				self.cursor.execute("DROP TABLE IF EXISTS "+ self.table_name)
				self.cursor.close()
				del self.cursor
		except Exception as e:
			raise e
		finally:
			self.conn.close()
			self.flag_conn_open = False		

	def start_drain(self):
		queueDrain = threading.Thread(target=self._drain)
		queueDrain.daemon = True
		queueDrain.start()
		queueDrain.join()
