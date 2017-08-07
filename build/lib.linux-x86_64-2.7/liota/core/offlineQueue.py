# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------#
#  Copyright © 2015-2016 VMware, Inc. All Rights Reserved.                    #
#                                                                             #
#  Licensed under the BSD 2-Clause License (the “License”); you may not use   #
#  this file except in compliance with the License.                           #
#                                                                             #
#  The BSD 2-Clause License                                                   #
#                                                                             #
#  Redistribution and use in source and binary forms, with or without         #
#  modification, are permitted provided that the following conditions are met:#
#                                                                             #
#  - Redistributions of source code must retain the above copyright notice,   #
#      this list of conditions and the following disclaimer.                  #
#                                                                             #
#  - Redistributions in binary form must reproduce the above copyright        #
#      notice, this list of conditions and the following disclaimer in the    #
#      documentation and/or other materials provided with the distribution.   #
#                                                                             #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"#
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE  #
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE #
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE  #
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR        #
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF       #
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS   #
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN    #
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)    #
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF     #
#  THE POSSIBILITY OF SUCH DAMAGE.                                            #
# ----------------------------------------------------------------------------#

import logging
from collections import deque
import threading
import time
from liota.dcc_comms.dcc_comms import DCCComms

log = logging.getLogger(__name__)

class offlineQueue:
	def __init__(self, size, drop_oldest, comms, draining_frequency=0):
		"""
			:param size: size of the offline_queue, if negative implies infinite.
			:param drop_oldest: if True oldest data will be dropped after size of queue is exceeded. 
			:param comms: comms instance of DCCComms
			:param draining_frequency: frequency with which data will be published after internet connectivity established.
		"""
		if not isinstance(size, int):
			log.error("Size is expected of int type.")
			raise TypeError("Size is expected of int type.")
		if not isinstance(drop_oldest, bool):
			log.error("drop_oldest/newest is expected of bool type.")
			raise TypeError("drop_oldest is expected of bool type.")
		if not isinstance(comms, DCCComms):
			log.error("DCCComms object is expected.")
			raise TypeError("DCCComms object is expected.")
		if not isinstance(draining_frequency, float) and not isinstance(draining_frequency, int):
			log.error("draining_frequency is expected of float or int type.")
			raise TypeError("draining_frequency is expected of float or int type.")
		try: 
			assert size!=0 and draining_frequency>=0
		except AssertionError as e:
			log.error("Size can't be zero, draining_frequency can't be negative.")
			raise e
		self.size = size
		self.drop_oldest = drop_oldest
		if (self.size>0 and drop_oldest):
			self.d = deque(maxlen=self.size)
		else:
			self.d = deque()
		self.comms = comms
		self.draining_frequency = draining_frequency
		self._offlineQLock = threading.Lock()
		
	def append(self, data):
		if (self.size<0):	#for infinite length deque
			self.d.append(data)
		elif (self.size>0 and self.drop_oldest): #for deque with drop_oldest=True
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(self.d[0]))
			self.d.append(data)
		else:									#for deque with drop_oldest=False
			if len(self.d) is self.size:
				log.info("Message dropped: {}".format(data))
			else:
				self.d.append(data)

	def _drain(self):
		self._offlineQLock.acquire()
		while self.d:
			data = self.d.pop()
			log.info("Data Drain: {}".format(data))
			self.comms.send(data)
			if self.d:
				data1 = self.d.popleft()
				log.info("Data Drain: {}".format(data))
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
