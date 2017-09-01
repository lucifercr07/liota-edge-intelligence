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
from liota.dccs.wavefront import Wavefront
from liota.dcc_comms.mqtt_dcc_comms import MqttDccComms 
from liota.lib.transports.mqtt import MqttMessagingAttributes, QoSDetails
from liota.lib.utilities.identity import Identity
from liota.lib.utilities.tls_conf import TLSConf
from liota.entities.metrics.metric import Metric 
from liota.dccs.dcc import RegistrationFailure
from liota.edge_component.rule_component_one_metric import RuleEdgeComponent 
from liota.entities.edge_systems.dell5k_edge_system  import Dell5KEdgeSystem
from liota.lib.utilities.offline_buffering import BufferingParams
import random

config = {}
execfile('../sampleProp1.conf', config)

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
	return round(random.uniform(20.0,35.0),2)

def collect_rpm_vib():
	l = [get_rpm(), get_vibration()]
	return l

def collect_rpm_vib_temp():
	l = [get_rpm(), get_vibration(), get_temp()]
	return l

def action_actuator(value):
	print value

if __name__ == '__main__':

	offline_buffering = BufferingParams(persistent_storage=True, queue_size=-1, data_drain_size=10, draining_frequency=1)
	edge_system = Dell5KEdgeSystem(config['EdgeSystemName'])
	#  Encapsulates Identity
	identity = Identity(root_ca_cert=config['broker_root_ca_cert'], username=config['broker_username'], password=['broker_password'],
						cert_file=None, key_file=None)
	# Encapsulate TLS parameters
	tls_conf = TLSConf(config['cert_required'], config['tls_version'], config['cipher'])
	# Encapsulate QoS related parameters
	qos_details = QoSDetails(config['in_flight'], config['queue_size'], config['retry'])

	#  Connecting to AWSIoT
	#  AWSIoT broker doesn't support session persistence.  So, always use "clean_session=True"
	#  Custom Publish Topic for an EdgeSystem
	mqtt_msg_attr = MqttMessagingAttributes(pub_topic=config['CustomPubTopic'])

	wavefront = Wavefront(MqttDccComms(edge_system_name=edge_system.name,
							  url=config['BrokerIP'], port=config['BrokerPort'], identity=identity,
							  tls_conf=tls_conf,
							  qos_details=qos_details,
							  clean_session=True,
							  protocol=config['protocol'], transport=['transport'],
							  conn_disconn_timeout=config['ConnectDisconnectTimeout'],
							  mqtt_msg_attr=mqtt_msg_attr), buffering_params=offline_buffering)

	try:
		# create a System object encapsulating the particulars of a IoT System
		# argument is the name of this IoT System
		# resister the IoT System with the graphite instance
		# this call creates a representation (a Resource) in graphite for this IoT System with the name given
		reg_edge_system = wavefront.register(edge_system)
		
		rule_temp_metric = Metric(
			name="thermistor.temperature",
			unit=None,
			interval=1,
			aggregation_size=1,
			sampling_function=get_rpm
		)
		
		temp_limit=25
		ModelRule = lambda x : 1 if (x>=temp_limit) else 0
		exceed_limit = 1								#number of consecutive times a limit can be exceeded

		edge_component = RuleEdgeComponent(ModelRule, exceed_limit, actuator_udm=action_actuator)
		rule_reg_temp_metric = edge_component.register(rule_temp_metric)
		rule_reg_temp_metric.start_collecting()
		
	except RegistrationFailure:
		print "Registration to graphite failed"


