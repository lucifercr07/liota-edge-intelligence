from liota.core.package_manager import LiotaPackage

dependencies = ["graphite", "examples/rule_package"]

class PackageClass(LiotaPackage):
	def create_udm(self, windmill_model):
		modelRule = windmill_model.modelRule
		
		def get_rpm():
			return windmill_model.get_rpm()

		def get_vib():
			return windmill_model.get_vib()

		def get_action():
			print("Action: ", windmill_model.modelRule(get_rpm))

		self.get_action = get_action

	def run(self, registry):
		from liota.entities.metrics.metric import Metric

		graphite = registry.get("graphite")
		windmill_simulator = registry.get("windmill_simulator")
		graphite_windmill = graphite.register(windmill_simulator)

		self.create_udm(windmill_model=windmill_simulator)

		self.metrics = []

		metric_name = "model.rpm"
		
		rpm = Metric(
			name = metric_name,
			unit = None,
			interval=1,
			aggregation_size=1,
			sampling_function=self.get_rpm	#how to plot rpm and actions taken along with it at once??
		)

		reg_rpm = graphite.register(rpm)
        graphite.create_relationship(graphite_metric_simulator, reg_rpm)
        reg_rpm.start_collecting()
        self.metrics.append(reg_rpm)

        def clean_up(self):
        	for metric in self.metrics:
        		metric.stop_collecting()


