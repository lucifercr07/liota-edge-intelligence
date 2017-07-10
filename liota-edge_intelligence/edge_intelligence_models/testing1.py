import tensorflow as tf 
import os
import pandas as pd
import itertools
import numpy as np

BASE_DIRECTORY =  "/home/prasha/git_repo/liota-edge-intelligence/liota-edge_intelligence/edge_intelligence_models"
MODEL_BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'saved-model')

TESTING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-test-data.csv')
PREDICT_FILE = os.path.join(BASE_DIRECTORY, 'windmill-predict-data.csv')

COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM"]
LABEL = "windmill.TurnOff"

def input_fn(train_data_set):
    features = {k: tf.constant(train_data_set[k].values) for k in FEATURES}
    label = tf.constant(train_data_set[LABEL].values)
    #print("FEATURES: ",features,label)
    return features, label

sess = tf.Session()
test = pd.read_csv(TESTING_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)

feature_cols = [tf.contrib.layers.real_valued_column(k)
                  for k in FEATURES]

optimizer = tf.train.FtrlOptimizer(
    learning_rate=0.1,
    l1_regularization_strength=1.0,
    l2_regularization_strength=1.0)

predict = pd.read_csv(PREDICT_FILE, names=COLUMNS, skipinitialspace = True, skiprows=1)

e = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, optimizer=optimizer, model_dir=MODEL_BASE_DIRECTORY)

ev = e.evaluate(input_fn=lambda:input_fn(test), steps=1)
loss_score = ev["loss"]

print("Loss: {0:f}".format(loss_score))

def f():
	return np.array([[45],[1]],dtype=np.int64)

y = e.predict(input_fn=f)

print(list(y))

#predictions= list(itertools.islice(y,6))
#print("Predictions: {}".format(str(predictions)))

