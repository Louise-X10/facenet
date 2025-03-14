# MIT License
# 
# Copyright (c) 2017 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Variational autoencoder based on the paper 
'Deep Feature Consistent Variational Autoencoder'
(https://arxiv.org/pdf/1610.00291.pdf)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tf_slim as slim
import generative.models.vae_base  # @UnresolvedImport


class Vae(generative.models.vae_base.Vae):
  
    def __init__(self, latent_variable_dim):
        super(Vae, self).__init__(latent_variable_dim, 64)
  
    def encoder(self, images, is_training):
        activation_fn = leaky_relu  # tf.nn.relu
        weight_decay = 0.0
        with tf.compat.v1.variable_scope('encoder'):
            with slim.arg_scope([slim.batch_norm],
                                is_training=is_training):
                with slim.arg_scope([slim.conv2d, slim.fully_connected],
                                    weights_initializer=tf.compat.v1.truncated_normal_initializer(stddev=0.1),
                                    weights_regularizer=tf.keras.regularizers.l2(0.5 * (weight_decay)),
                                    normalizer_fn=slim.batch_norm,
                                    normalizer_params=self.batch_norm_params):
                    net = slim.conv2d(images, 32, [4, 4], 2, activation_fn=activation_fn, scope='Conv2d_1')
                    net = slim.conv2d(net, 64, [4, 4], 2, activation_fn=activation_fn, scope='Conv2d_2')
                    net = slim.conv2d(net, 128, [4, 4], 2, activation_fn=activation_fn, scope='Conv2d_3')
                    net = slim.conv2d(net, 256, [4, 4], 2, activation_fn=activation_fn, scope='Conv2d_4')
                    net = slim.flatten(net)
                    fc1 = slim.fully_connected(net, self.latent_variable_dim, activation_fn=None, normalizer_fn=None, scope='Fc_1')
                    fc2 = slim.fully_connected(net, self.latent_variable_dim, activation_fn=None, normalizer_fn=None, scope='Fc_2')
        return fc1, fc2
      
    def decoder(self, latent_var, is_training):
        activation_fn = leaky_relu  # tf.nn.relu
        weight_decay = 0.0 
        with tf.compat.v1.variable_scope('decoder'):
            with slim.arg_scope([slim.batch_norm],
                                is_training=is_training):
                with slim.arg_scope([slim.conv2d, slim.fully_connected],
                                    weights_initializer=tf.compat.v1.truncated_normal_initializer(stddev=0.1),
                                    weights_regularizer=tf.keras.regularizers.l2(0.5 * (weight_decay)),
                                    normalizer_fn=slim.batch_norm,
                                    normalizer_params=self.batch_norm_params):
                    net = slim.fully_connected(latent_var, 4096, activation_fn=None, normalizer_fn=None, scope='Fc_1')
                    net = tf.reshape(net, [-1,4,4,256], name='Reshape')
                    
                    net = tf.image.resize(net, size=(8,8), name='Upsample_1', method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
                    net = slim.conv2d(net, 128, [3, 3], 1, activation_fn=activation_fn, scope='Conv2d_1')
            
                    net = tf.image.resize(net, size=(16,16), name='Upsample_2', method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
                    net = slim.conv2d(net, 64, [3, 3], 1, activation_fn=activation_fn, scope='Conv2d_2')
            
                    net = tf.image.resize(net, size=(32,32), name='Upsample_3', method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
                    net = slim.conv2d(net, 32, [3, 3], 1, activation_fn=activation_fn, scope='Conv2d_3')
            
                    net = tf.image.resize(net, size=(64,64), name='Upsample_4', method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
                    net = slim.conv2d(net, 3, [3, 3], 1, activation_fn=None, scope='Conv2d_4')
                
        return net
      
def leaky_relu(x):
    return tf.maximum(0.1*x,x)
  