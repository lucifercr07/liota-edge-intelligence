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

from linux_metrics import cpu_stat, mem_stat
from liota.dccs.graphite import Graphite
from liota.dcc_comms.socket_comms import SocketDccComms 
from liota.entities.metrics.metric import Metric 
from liota.dccs.dcc import RegistrationFailure
from liota.edge_component.lambda_edge_component_generalisation import RuleEdgeComponent 
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

def get_vibration():
	return round(random.uniform(0.480,0.7),3)

def get_temp():
	return round(random.uniform(33.0,40.0),2)

def action_actuator(value):
	print value

if __name__ == '__main__':

	

	try:
		# create a System object encapsulating the particulars of a IoT System
		# argument is the name of this IoT System
		edge_system = Dell5KEdgeSystem(config['EdgeSystemName'])

		# resister the IoT System with the graphite instance
		# this call creates a representation (a Resource) in graphite for this IoT System with the name given
		
		
		rule_rpm_metric = Metric(
			name="rpm",
			unit=None,
			interval=1,
			aggregation_size=1,
			sampling_function=get_rpm
		)
		
		rpm_limit=45
		vib_limit = 0.500
		temp_limit =35.00
		ModelRule = lambda rpm,vib,temp : 1 if (rpm>=rpm_limit and vib>=vib_limit and temp>=temp_limit) else 0
		exceed_limit = 1								#number of consecutive times a limit can be exceeded

		edge_component = RuleEdgeComponent(ModelRule, exceed_limit,'temp', actuator_udm=action_actuator)
		graphite = Graphite(SocketDccComms(ip=config['GraphiteIP'],port=8080),edge_component)
		reg_edge_system = graphite.register(edge_system)
		
		rule_reg_rpm_metric = graphite.register(rule_rpm_metric)
		rule_reg_rpm_metric.start_collecting()

		rule_vib_metric = Metric(
			name="vib",
			unit=None,
			interval=2,
			aggregation_size=1,
			sampling_function=get_vibration
		)

		rule_reg_vib_metric = graphite.register(rule_vib_metric)
		rule_reg_vib_metric.start_collecting()

		rule_temp_metric = Metric(
			name="temp",
			unit=None,
			interval=3,
			aggregation_size=1,
			sampling_function=get_temp
		)

		rule_reg_temp_metric = graphite.register(rule_temp_metric)
		rule_reg_temp_metric.start_collecting()

		
	except RegistrationFailure:
		print "Registration to graphite failed"
