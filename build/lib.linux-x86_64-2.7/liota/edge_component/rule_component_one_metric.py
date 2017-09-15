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
import numpy as np
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric
import types

log = logging.getLogger(__name__)

class RuleEdgeComponent(EdgeComponent):
	def __init__(self, model_rule, exceed_limit_consecutive, actuator_udm):
		if model_rule is None:
			raise TypeError("Model rule must be specified.")

		if not isinstance(model_rule, types.LambdaType):
			raise TypeError("Model rule must be a lambda function.")

		if model_rule.__name__ != "<lambda>":
			raise TypeError("Model rule must be a lambda function.")			

		if type(exceed_limit_consecutive) is not int:
			raise ValueError("exceed_limit should be a integer value.")

		if not isinstance(actuator_udm, types.FunctionType):
			raise TypeError("Model rule must be a function.")

		self.model_rule = model_rule
		self.actuator_udm = actuator_udm
		self.exceed_limit = exceed_limit_consecutive
		self.counter = 0

	def register(self, entity_obj):
		if isinstance(entity_obj, Metric):
			return RegisteredMetric(entity_obj, self, None)
		else:
			return RegisteredEntity(entity_obj, self, None)

	def create_relationship(self, reg_entity_parent, reg_entity_child):
		pass 	

	def process(self, message):
		result = self.model_rule(*message)
		self.counter = 0 if(result==0) else self.counter+1
		if(self.counter>=self.exceed_limit):
			self.actuator_udm(1)
			self.counter=0
		else:
			self.actuator_udm(0)


	def _format_data(self, reg_metric):
		met_cnt = reg_metric.values.qsize()
		metric = []
		if met_cnt == 0:
			return
		if met_cnt == 1:
			print "HI: ", reg_metric.ref_entity.name
			m = reg_metric.values.get(block=True)
			metric.append(m[1])
		else:
			while met_cnt !=0:
				m = reg_metric.values.get(block=True)
				if m is not None:
					metric.append(m)
				met_cnt-=1
		return metric	

	def build_model(self):
		pass	

	def load_model(self):
		pass

	def set_properties(self, reg_entity, properties):
		pass

	def unregister(self):
		pass


