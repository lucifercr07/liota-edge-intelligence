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

import tensorflow
import logging
import numpy as np
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric

log = logging.getLogger(__name__)


class TensorFlowEdgeComponent(EdgeComponent):

    def __init__(self, model_path, actuator_udm):
        super(TensorFlowEdgeComponent, self).__init__(model_path, actuator_udm)
        self.model = None
        self.load_model()

    def load_model(self):
        with tf.gfile.GFile(frozen_model_path, "rb") as f:
            model_graph_def = tf.GraphDef()
            model_graph_def.ParseFromString(f.read())

        # built-in function to import a model_graph_def
        with tf.Graph().as_default() as model_graph:
            tf.import_graph_def(
                model_graph_def, 
                input_map=None, 
                return_elements=None, 
                name="prefix", 
                op_dict=None, 
                producer_op_list=None
            )
        log.info("Tensor Flow Model Loaded")    
        return model_graph

    def register(self, entity_obj):
        if isinstance(entity_obj, Metric):
            return RegisteredMetric(entity_obj, self, None)
        else:
            return RegisteredEntity(entity_obj, self, None)

    def create_relationship(self, reg_entity_parent, reg_entity_child):
        reg_entity_child.parent = reg_entity_parent

    def process(self, message):
        # TODO: Apply model and return result
        self.actuator_udm(self.model.predict(message)[0])

    def _format_data(self, reg_metric):
        # TODO: get values out of reg_metric and return values
        pass

    def set_properties(self, reg_entity, properties):
        super(TensorFlowEdgeComponent, self).set_properties(reg_entity, properties)

    def unregister(self, entity_obj):
        pass

    def build_model(self):
        pass


