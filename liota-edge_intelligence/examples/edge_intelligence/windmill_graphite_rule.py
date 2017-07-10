from linux_metrics import cpu_stat, mem_stat
from liota.dccs.graphite import Graphite
from liota.dcc_comms.socket_comms import SocketDccComms 
from liota.entities.metrics.metric import Metric 
from liota.dccs.dcc import RegistrationFailure
from liota.edge_component.rule_edge_component import RuleEdgeComponent 
from liota.entities.edge_systems.dell5k_edge_system  import Dell5KEdgeSystem
import random

config = {}
execfile('../sampleProp.conf', config)

def read_cpu_procs():
	return cpu_stats.procs_running()

def read_cpu_utilization(sample_duration_sec=1):
	cpu_pcts = cpu_stat.cpu_percents(sample_duration_sec)
	return round((100 - cpu_pcts['idle']), 2)


def read_mem_free():
	total_mem = round(mem_stat.mem_stats()[1], 4)
	free_mem = round(mem_stat.mem_stats()[3], 4)
	mem_free_percent = ((total_mem - free_mem) / total_mem) * 100
	return round(mem_free_percent, 2)

def get_rpm():
	return random.randint(42,54)

def action_actuator(value):
	print value

if __name__ == '__main__':

	graphite = Graphite(SocketDccComms(ip=config['GraphiteIP'],
									   port=8080))

	try:
		# create a System object encapsulating the particulars of a IoT System
		# argument is the name of this IoT System
		edge_system = Dell5KEdgeSystem(config['EdgeSystemName'])

		# resister the IoT System with the graphite instance
		# this call creates a representation (a Resource) in graphite for this IoT System with the name given
		reg_edge_system = graphite.register(edge_system)
		
		rule_rpm_metric = Metric(
			name="windmill.RPM",
			unit=None,
			interval=1,
			aggregation_size=1,
			sampling_function=get_rpm
		)

		edge_component = RuleEdgeComponent(config['ModelRule'], actuator_udm=action_actuator)
		rule_reg_rpm_metric = edge_component.register(rule_rpm_metric)
		rule_reg_rpm_metric.start_collecting()

	except RegistrationFailure:
		print "Registration to graphite failed"

