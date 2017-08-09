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

import pint
import math
import Queue
import random
from linux_metrics import cpu_stat, mem_stat

from liota.dccs.graphite import Graphite
from liota.entities.metrics.metric import Metric
#from liota.entities.devices.sensor_tag import Sensors, SensorTagCollector
from liota.entities.edge_systems.dell5k_edge_system import Dell5KEdgeSystem
from liota.dcc_comms.socket_comms import SocketDccComms
from liota.dccs.dcc import RegistrationFailure
from liota.edge_component.tf_edge_component import TensorFlowEdgeComponent 

# getting values from conf file
config = {}
execfile('../sampleProp.conf', config)

# create a pint unit registry
ureg = pint.UnitRegistry()

rpm_model_queue = Queue.Queue()


def read_cpu_procs():
    return cpu_stat.procs_running()


def read_cpu_utilization(sample_duration_sec=1):
    cpu_pcts = cpu_stat.cpu_percents(sample_duration_sec)
    return round((100 - cpu_pcts['idle']), 2)


def read_mem_free():
    total_mem = round(mem_stat.mem_stats()[1], 4)
    free_mem = round(mem_stat.mem_stats()[3], 4)
    mem_free_percent = ((total_mem - free_mem) / total_mem) * 100
    return round(mem_free_percent, 2)


def get_ambient_temperature(sensor_tag_collector):
    return sensor_tag_collector.get_temperature()[0]


def get_relative_humidity(sensor_tag_collector):
    return sensor_tag_collector.get_humidity()[1]


def get_pressure(sensor_tag_collector):
    # 1 millibar = 100 Pascal
    return sensor_tag_collector.get_barometer()[1] * 100


def get_light_level(sensor_tag_collector):
    return sensor_tag_collector.get_light_level()


def get_vibration_level(sensor_tag_collector):
    # Accelerometer x,y,z in g
    x, y, z = sensor_tag_collector.get_accelerometer()
    # Magnitude of acceleration
    # ∣a⃗∣=√ (x*x+y*y+z*z)
    vib = math.sqrt((x * x + y * y + z * z))
    return vib

'''
def get_rpm(sensor_tag_collector):
    # RPM of Z-axis
    # Average of 5 samples
    _rpm_list = []
    while True:
        if len(_rpm_list) == 5:
            rpm = 0
            for _ in _rpm_list:
                rpm += _
            rpm = int(rpm / 5)
            break
        else:
            z_degree = sensor_tag_collector.get_gyroscope()[2]
            # (°/s to RPM)
            _rpm_list.append(int((abs(z_degree) * 0.16667)))
    rpm_model_queue.put(rpm)
    return rpm
'''

def get_rpm_for_model():
    return rpm_model_queue.get(block=True)


def action_actuator(value):
    print value

#collecting list of all metrics required for windmill model in order rpm,vibration,
#ambient temperature and humidity
def collecting_all_metrics():
    list_of_metrics=[get_rpm(),get_vibration_level(),get_ambient_temperature(),get_relative_humidity()]
    return list_of_metrics

def get_rpm():
    return random.randint(10,25)

def get_vibration():
    return random.uniform(0.300,0.600)

def collect_two_metrics():
	list_metric = [get_rpm(),get_vibration()]
	return list_metric

# ---------------------------------------------------------------------------------------
# In this example, we demonstrate how metrics collected from a SensorTag device over BLE
# can be directed to graphite data center component using Liota.
# The program illustrates the ease of use Liota brings to IoT application developers.

if __name__ == '__main__':

    # create a data center object, graphite in this case, using websocket as a transport layer
    graphite = Graphite(SocketDccComms(ip=config['GraphiteIP'],
                                       port=8080))

    try:
        # create a System object encapsulating the particulars of a IoT System
        # argument is the name of this IoT System
        edge_system = Dell5KEdgeSystem(config['EdgeSystemName'])

        # resister the IoT System with the graphite instance
        # this call creates a representation (a Resource) in graphite for this IoT System with the name given
        reg_edge_system = graphite.register(edge_system)

        # Operational metrics of EdgeSystem
        cpu_utilization_metric = Metric(
            name="windmill.CPU_Utilization",
            unit=None,
            interval=10,
            aggregation_size=2,
            sampling_function=read_cpu_utilization
        )
        reg_cpu_utilization_metric = graphite.register(cpu_utilization_metric)
        graphite.create_relationship(reg_edge_system, reg_cpu_utilization_metric)
        # call to start collecting values from the device or system and sending to the data center component
        reg_cpu_utilization_metric.start_collecting()

        cpu_procs_metric = Metric(
            name="windmill.CPU_Process",
            unit=None,
            interval=6,
            aggregation_size=8,
            sampling_function=read_cpu_procs
        )
        reg_cpu_procs_metric = graphite.register(cpu_procs_metric)
        graphite.create_relationship(reg_edge_system, reg_cpu_procs_metric)
        reg_cpu_procs_metric.start_collecting()

        mem_free_metric = Metric(
            name="windmill.Memory_Free",
            unit=None,
            interval=10,
            sampling_function=read_mem_free
        )
        reg_mem_free_metric = graphite.register(mem_free_metric)
        graphite.create_relationship(reg_edge_system, reg_mem_free_metric)
        reg_mem_free_metric.start_collecting()

        tf_rpm_metric = Metric(
            name="windmill.RPM",
            unit=None,
            interval=1,
            aggregation_size=1,
            sampling_function=get_rpm
        )

        edge_component = TensorFlowEdgeComponent(config['ModelPath'], config['Features'], actuator_udm=action_actuator)
        tf_reg_two_metric = edge_component.register(tf_rpm_metric)
        tf_reg_two_metric.start_collecting()

    except RegistrationFailure:
        print "Registration to graphite failed"
        sensor_tag_collector.stop()
