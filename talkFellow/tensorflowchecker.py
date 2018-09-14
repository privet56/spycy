import tensorflow as tf
import numpy as np
from seq2seq import models
from seq2seq.training import utils as training_utils
from seq2seq.tasks.inference_task import InferenceTask, unbatch_dict

hello = tf.constant('Hello, TensorFlow!')
sess = tf.Session()
print(sess.run(hello))
