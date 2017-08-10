from liota.core.package_manager import LiotaPackage
import logging
import Queue

log = logging.getLogger(__name__)
hdlr = logging.FileHandler('/var/log/liota/liota.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 

dependencies = ["graphite", "sklearn_edge_component", "examples/windmill_simulator"]

action_taken = Queue.Queue()

class PackageClass(LiotaPackage):
	def create_udm(self, windmill_model):
		
		def get_rpm():
			return windmill_model.get_rpm()

		def get_vib():
			return windmill_model.get_vib()

		def get_action(value):
			log.info("Action: {}".format(value))
			action_taken.put(value)

		def get_action_taken():
			return action_taken.get(block=True)

		self.get_rpm = get_rpm
		self.get_action = get_action
		self.get_action_taken = get_action_taken

	def run(self, registry):
		from liota.entities.metrics.metric import Metric

		windmill_simulator = registry.get("windmill_simulator")
		sklearn_edge_component = registry.get("sklearn_edge_component")
		graphite = registry.get("graphite")
		graphite_windmill = graphite.register(windmill_simulator)

		self.create_udm(windmill_model=windmill_simulator)
		
		sklearn_edge_component.actuator_udm = self.get_action
		
		self.metrics = []

		metric_name = "edge_sklearn.rpm"
		
		rpm = Metric(
			name = metric_name,
			unit = None,
			interval=1,
			aggregation_size=1,
			sampling_function=self.get_rpm
		)

		reg_windmill_rpm = graphite.register(rpm)
		graphite.create_relationship(graphite_windmill, reg_windmill_rpm)
		reg_rpm = sklearn_edge_component.register(rpm)
		reg_rpm.start_collecting()
		reg_windmill_rpm.start_collecting()
		self.metrics.append(reg_windmill_rpm)

		metric_name1 = "edge_sklearn.action"

		action_taken = Metric(
			name = metric_name1,
			unit = None,
			interval=1,
			aggregation_size=1,
			sampling_function=self.get_action_taken
		)
		
		reg_windmill_action = graphite.register(action_taken)
		graphite.create_relationship(graphite_windmill, reg_windmill_action)
		reg_windmill_action.start_collecting()
		self.metrics.append(reg_windmill_action)
        
        def clean_up(self):
        	for metric in self.metrics:
        		metric.stop_collecting()


