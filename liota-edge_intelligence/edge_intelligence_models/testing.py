import tensorflow as tf 
import pandas as pd 
import numpy as np 
import os
import itertools
import tempfile
from tensorflow.python.framework import graph_util
from tensorflow.contrib.learn.python.learn.utils import input_fn_utils

#tf.logging.set_verbosity(tf.logging.INFO)

BASE_DIRECTORY =  "/home/prasha/git_repo/liota-edge-intelligence/liota-edge_intelligence/edge_intelligence_models"
MODEL_BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'saved-model')
TRAINING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-train-data.csv')

COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM"]
LABEL = "windmill.TurnOff"


def input_fn(train_data_set):
    features = {k: tf.constant(train_data_set[k].values) for k in FEATURES}
    label = tf.constant(train_data_set[LABEL].values)
    return features, label

def build_model():
    train = pd.read_csv(TRAINING_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)

    feature_cols = [tf.contrib.layers.real_valued_column(k)
                  for k in FEATURES]
    
    optimizer = tf.train.FtrlOptimizer(
        learning_rate=0.1,
        l1_regularization_strength=1.0,
        l2_regularization_strength=1.0)

    e = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, optimizer=optimizer, model_dir=MODEL_BASE_DIRECTORY)
    
    e.fit(input_fn=lambda:input_fn(train),steps=200)
    return e 



with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    mymodel = build_model()
    
    #saver = tf.train.Saver()

    #saver.save(sess, os.path.join(MODEL_BASE_DIRECTORY, "testing_model"))

    '''
    loss_score = ev["loss"]

    print("Loss: {0:f}".format(loss_score))

    y = mymodel.predict(input_fn=lambda:input_fn(predict))

    predictions= list(itertools.islice(y,6))
    print("Predictions: {}".format(str(predictions)))
    '''
    
    '''
    freezeGraph(TEMP_MODEL_PATH, MODEL_BASE_DIRECTORY)    

    g = load_graph(os.path.join(MODEL_BASE_DIRECTORY, "frozen_model.pb"))

    print("Printing Operations in the graph...")
    for op in g.get_operations():
        print(str(op))
    
    output = g.get_tensor_by_name('prefix/linear/linear/windmill.RPM/ExpandDims/dim:0')
    x = g.get_tensor_by_name('prefix/linear/windmill.Vibration/weight:0')
    with tf.Session(graph=g) as sess:
        y_out = sess.run(output, feed_dict={x: [3, 5, 7, 4, 5, 1, 1, 1, 1, 1]})
        print(y_out)  # [[ False ]] Yay, it works!

    '''



