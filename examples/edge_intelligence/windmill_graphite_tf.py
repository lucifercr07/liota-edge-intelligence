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

import math
import Queue
import random

from liota.dccs.graphite import Graphite
from liota.entities.metrics.metric import Metric
from liota.entities.edge_systems.dell5k_edge_system import Dell5KEdgeSystem
from liota.dcc_comms.socket_comms import SocketDccComms
from liota.dccs.dcc import RegistrationFailure
from liota.edge_component.tensorflow_edge_component import TensorFlowEdgeComponent 

# getting values from conf file
config = {}
execfile('../sampleProp.conf', config)

def action_actuator(value):
    print value

def get_rpm():
    return random.randint(10,25)

def get_vibration():
    return round(random.uniform(0.480,0.7),3)

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
        
        tf_rpm_metric = Metric(
            name="windmill.RPM",
            unit=None,
            interval=1,
            aggregation_size=1,
            sampling_function=get_rpm
        )

        edge_component = TensorFlowEdgeComponent(config['ModelPath'], actuator_udm=action_actuator)
        tf_reg_two_metric = edge_component.register(tf_rpm_metric)
        tf_reg_two_metric.start_collecting()

    except RegistrationFailure:
        print "Registration to graphite failed"
