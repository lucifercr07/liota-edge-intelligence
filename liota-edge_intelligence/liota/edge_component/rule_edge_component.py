import logging
import numpy as np
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric

log = logging.getLogger(__name__)

#rpm_limit=45

class RuleEdgeComponent(EdgeComponent):
	def __init__(self, model_rule, actuator_udm):
		self.model_rule = model_rule
		self.actuator_udm = actuator_udm

	def register(self, entity_obj):
		if isinstance(entity_obj, Metric):
			return RegisteredMetric(entity_obj, self, None)
		else:
			return RegisteredEntity(entity_obj, self, None)

	def create_relationship(self, reg_entity_parent, reg_entity_child):
		pass 	#when create relationship with graphite

	def process(self, message):
		self.actuator_udm(self.model_rule(message))
		#uncomment this if to stop only after 5 consecutive greater values than limit
		'''
		result,counter = 0,0
		while message is not None:
			result = self.model_rule(message)
			counter = 0 if(result==0) else counter+1
			if(counter>=5):
				self.actuator_udm(1)
			else:
				self.actuator_udm(0)
		'''
		
	def _format_data(self, reg_metric):
		met_cnt = reg_metric.values.qsize()
		if met_cnt == 0:
			return
		for _ in range(met_cnt):
			m = reg_metric.values.get(block=True)
			if m is not None:
				return m[1]

	def build_model(self):
		pass	

	def load_model(self):
		pass

	def set_properties(self, reg_entity, properties):
		pass

	def unregister(self):
		pass


