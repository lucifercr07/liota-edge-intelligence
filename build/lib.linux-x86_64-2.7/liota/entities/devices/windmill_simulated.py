import random
from liota.entities.devices.device import Device
from liota.lib.utilities.utility import systemUUID

class windmillSimulated(Device):
	def __init__(self, name, modelRule):
		super(windmillSimulated, self).__init__(
			name=name,
			entity_id=systemUUID().get_uuid(name),
            entity_type="windmillSimulated"
            )
		self.modelRule = modelRule

	def get_rpm():
		return random.randint(10,25)

	def get_vib():
		return round(random.uniform(0.480,0.7),3)

	def get_temp():
		return round(random.uniform(20.0,35.0),3)