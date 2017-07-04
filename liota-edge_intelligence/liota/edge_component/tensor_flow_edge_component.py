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

import tensorflow as tf
import pandas as pd
import itertools
import logging
import numpy as np
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric

log = logging.getLogger(__name__)
COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM", "windmill.Vibration"]
LABEL = "windmill.TurnOff"
def input_fn(train_data_set):
    features = {k: tf.constant(train_data_set[k].values) for k in FEATURES}
    label = tf.constant(train_data_set[LABEL].values)
    return features, label

class TensorFlowEdgeComponent(EdgeComponent):

    def __init__(self, model_path, actuator_udm):
        super(TensorFlowEdgeComponent, self).__init__(model_path, actuator_udm)
        self.model = None
        self.load_model(self.model_path)

    def load_model(self,model_path):
        with tf.Session() as sess:
            feature_cols = [tf.contrib.layers.real_valued_column(k) for k in FEATURES]
            optimizer = tf.train.FtrlOptimizer(
                learning_rate=0.1,
                l1_regularization_strength=1.0,
                l2_regularization_strength=1.0)
            predict = pd.read_csv(self.model_path, names=COLUMNS, skipinitialspace = True, skiprows=1)
            model = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, optimizer=optimizer, model_dir=self.model_path)
            return model

    def register(self, entity_obj):
        if isinstance(entity_obj, Metric):
            return RegisteredMetric(entity_obj, self, None)
        else:
            return RegisteredEntity(entity_obj, self, None)

    def create_relationship(self, reg_entity_parent, reg_entity_child):
        reg_entity_child.parent = reg_entity_parent

    def process(self, message):
        
        e = load_model()
        self.actuator_udm()

    def _format_data(self, reg_metric):
        met_cnt = reg_metric.values.qsize()
        if met_cnt == 0:
            return
        for _ in range(met_cnt):
            m = reg_metric.values.get(block=True)
            if m is not None:
                return np.array([m[1]]).reshape(-1, 1)

    def set_properties(self, reg_entity, properties):
        super(TensorFlowEdgeComponent, self).set_properties(reg_entity, properties)

    def unregister(self, entity_obj):
        pass

    def build_model(self):
        pass


