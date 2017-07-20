import tensorflow as tf 
import pandas as pd 
import numpy as np 
import os
import itertools
import tempfile
from tensorflow.python.framework import graph_util

#tf.logging.set_verbosity(tf.logging.INFO)

BASE_DIRECTORY =  r"C:\Users\pshubham\Documents\IoT\liota-edge_intelligence\edge_intelligence_models"
MODEL_BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'saved-windmill-model')
TEMP_MODEL_PATH = tempfile.mkdtemp(dir=MODEL_BASE_DIRECTORY)
TRAINING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-train-data.csv')
TESTING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-test-data.csv')
PREDICT_FILE = os.path.join(BASE_DIRECTORY, 'windmill-predict-data.csv')

COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM", "windmill.Vibration"]
LABEL = "windmill.TurnOff"

def input_fn(train_data_set):
    features = {k: tf.constant(train_data_set[k].values) for k in FEATURES}
    label = tf.constant(train_data_set[LABEL].values)
    return features, label

def build_model():
    train = pd.read_csv(TRAINING_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)
   
    train['type']='Train' #A flag for train data set
        
    feature_cols = [tf.contrib.layers.real_valued_column(k)
                  for k in FEATURES]
    optimizer = tf.train.FtrlOptimizer(
        learning_rate=0.1,
        l1_regularization_strength=1.0,
        l2_regularization_strength=1.0)

    e = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, optimizer=optimizer, model_dir=TEMP_MODEL_PATH)

    e.fit(input_fn=lambda:input_fn(train), steps=20)
    return e 

def freezeGraph(model_folder, save_folder):
    checkpoint = tf.train.get_checkpoint_state(model_folder)
    input_checkpoint = checkpoint.model_checkpoint_path

    output_graph_filepath = os.path.join(save_folder,"frozen_model.pb")
    
    output_node_names = [
    "linear/binary_logistic_head/predictions/zeros_like",
    "linear/binary_logistic_head/predictions/concat/axis",
    "linear/binary_logistic_head/predictions/concat",
    "linear/binary_logistic_head/predictions/logistic",
    "linear/binary_logistic_head/predictions/probabilities",
    "linear/binary_logistic_head/predictions/classes/dimension",
    "linear/binary_logistic_head/predictions/classes"]

    clear_devices = True

    saver = tf.train.import_meta_graph(input_checkpoint + '.meta', clear_devices=clear_devices)
    graph = tf.get_default_graph()
    input_graph_def = graph.as_graph_def()

    graph = tf.get_default_graph()
    input_graph_def = graph.as_graph_def()

    # We start a session and restore the graph weights
    with tf.Session() as sess:
        saver.restore(sess, input_checkpoint)

        # We use a built-in TF helper to export variables to constants
        output_graph_def = graph_util.convert_variables_to_constants(
            sess, # The session is used to retrieve the weights
            input_graph_def, # The graph_def is used to retrieve the nodes 
            output_node_names # The output node names are used to select the useful nodes
        ) 

        # Finally we serialize and dump the output graph to the filesystem
        with tf.gfile.GFile(output_graph_filepath, "wb") as f:
            f.write(output_graph_def.SerializeToString())
        print("%d ops in the final graph." % len(output_graph_def.node))


with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    mymodel = build_model()
    
    test = pd.read_csv(TESTING_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)
    predict = pd.read_csv(PREDICT_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)

    test['type']='Test'
    predict['type']='Predict'

    freezeGraph(TEMP_MODEL_PATH, MODEL_BASE_DIRECTORY)    

    
    ev = mymodel.evaluate(input_fn=lambda:input_fn(test), steps=1)
    
    loss_score = ev["loss"]

    print("Loss: {0:f}".format(loss_score))

    y = mymodel.predict(input_fn=lambda:input_fn(predict))

    predictions= list(itertools.islice(y,6))
    print("Predictions: {}".format(str(predictions)))




