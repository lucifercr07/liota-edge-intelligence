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
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric
from liota.lib.utilities.utility import getUTCmillis
import json
import inspect
import types
import Queue

log = logging.getLogger(__name__)

class RuleEdgeComponent(EdgeComponent):
	def __init__(self, model_rule, exceed_limit_consecutive, highest_interval_metric, actuator_udm):
		if model_rule is None:
			raise TypeError("Model rule must be specified.")

		if not isinstance(model_rule, types.LambdaType):
			raise TypeError("Model rule must be a lambda function.")

		if model_rule.__name__ != "<lambda>":
			raise TypeError("Model rule must be a lambda function.")			

		if type(exceed_limit_consecutive) is not int:
			raise ValueError("exceed_limit should be a integer value.")

		self.model_rule = model_rule
		self.no_args = model_rule.__code__.co_argcount
		self.actuator_udm = actuator_udm
		self.exceed_limit = exceed_limit_consecutive
		self.highest_interval_metric = highest_interval_metric
		self.counter = 0
		self.metric_list = []
		self.metrics_action = {}
		for i in range(self.no_args):
			self.metrics_action[inspect.getargspec(self.model_rule)[0][i]] = Queue.Queue()

	def register(self, entity_obj):
		if isinstance(entity_obj, Metric):
			return RegisteredMetric(entity_obj, self, None)
		else:
			return RegisteredEntity(entity_obj, self, None)

	def create_relationship(self, reg_entity_parent, reg_entity_child):
		pass 	

	def process(self, message):
		if message is not None:
			self.metric_list=[]
			print "Message in process: ", message
			result = self.model_rule(*message)
			
			metrics_message = {}
			
			for i in range(self.no_args):
				x = str(inspect.getargspec(self.model_rule)[0][i])
				metrics_message[x] = message[i]
			self.counter = 0 if(result==0) else self.counter+1
			if(self.counter>=self.exceed_limit):
				self.actuator_udm(1)
				metrics_message['result'] = 1
				self.counter=0
			else:
				self.actuator_udm(0)
				metrics_message['result'] = 0
			metrics_message['timestamp'] = getUTCmillis()
			json_data = json.dumps(metrics_message)
			return json_data

	def _format_data(self, reg_metric):
		met_cnt = reg_metric.values.qsize()
		if met_cnt == 0:
			return
		if met_cnt == 1:						
			m = reg_metric.values.get(block=True)
			self.metrics_action[reg_metric.ref_entity.name].put(m[1])
			if not self.metrics_action[self.highest_interval_metric].empty(): #we can check according to the interval one with highest interval as soon it gets fill start append
				for i in range(self.no_args):
					self.metric_list.append(self.metrics_action[inspect.getargspec(self.model_rule)[0][i]].get())
		if len(self.metric_list)!= self.no_args:
			return None
		else:
			return self.process(self.metric_list)	

	def build_model(self):
		pass	

	def load_model(self):
		pass

	def set_properties(self, reg_entity, properties):
		pass

	def unregister(self):
		pass


