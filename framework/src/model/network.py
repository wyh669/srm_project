import tensorflow as tf
#import tensorflow.contrib.tensorrt as trt
import numpy as np
import cv2 as cv
class Network(object):
    def __init__(self,graph_path = ""):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        with tf.Graph().as_default():
                output_graph_def = tf.GraphDef()
                with open(graph_path, "rb") as f:
                    output_graph_def.ParseFromString(f.read())
                    tf.import_graph_def(output_graph_def, name="")
                    self.sess = tf.Session(config= config)
                    self.input_tensor_name = self.sess.graph.get_tensor_by_name("init_1/input:0")
                    self.output_tensor_name = self.sess.graph.get_tensor_by_name("out_1/output:0")
    def __call__(self,x):
        '''
        description: given the input x, predict its class probability.
        x is an image in gray scale ranges from 0 to 255.
        
        return: [0.2, 0.8] the score of a class. first axis means background, the second is the score of number.
        '''
        assert len(x.shape) == 2
        x = cv.resize(x,(32,32))
        x = x / 127.5 - 1
        x = x[np.newaxis,:,:,np.newaxis]
        pred = self.sess.run(self.output_tensor_name,feed_dict={self.input_tensor_name:x})
        pred = np.exp(pred) / np.sum(np.exp(pred))
        return pred
        
