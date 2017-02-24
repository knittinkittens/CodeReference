#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 13:09:10 2017

This code was basically adapted (*cough copied cough*) from @jasonbaldridge's
try-tf example, but I rewrote it for myself for the sake of learning 
how to use tf and a few changes to make it python3 friendly.

"""
#==============================================================================
# Package imports and contstant declarations
#==============================================================================
from matplotlib import pyplot as plt
from matplotlib import colors
from sklearn import datasets
import tensorflow as tf
import pandas as pd
import numpy as np

num_labels = 2      # Number of labels
batch_size = 100    # Number of training samples to use per training step
num_epochs = 100    # Epochs: passes over the training data
num_hidden = 5      # Number of nodes in the hidden layer

#==============================================================================
# Define plotting function
#==============================================================================
def plot(X,Y,pred_func):
    # determine canvas borders
    mins = np.amin(X,0); 
    mins = mins - 0.1*np.abs(mins);
    maxs = np.amax(X,0); 
    maxs = maxs + 0.1*maxs;

    ## generate dense grid
    xs,ys = np.meshgrid(np.linspace(mins[0,0],maxs[0,0],300), 
            np.linspace(mins[0,1], maxs[0,1], 300));


    # evaluate model on the dense grid
    Z = pred_func(np.c_[xs.flatten(), ys.flatten()]);
    Z = Z.reshape(xs.shape)

    # Plot the contour and training examples
    plt.contourf(xs, ys, Z, cmap=plt.cm.Spectral)
    plt.scatter(X[:, 0], X[:, 1], c=Y[:,1], s=50,
            cmap=colors.ListedColormap(['orange', 'blue']))
    plt.show()

#==============================================================================
#  Initialize training dataset
#==============================================================================
X, y = datasets.make_moons(2000, noise=0.20)
X = pd.DataFrame(X, columns = ['x0', 'x1'])
X['y'] = y

train_size = X.shape[0]
num_features = X.shape[1] - 1

fvecs = X[['x0', 'x1']].astype(float).as_matrix()
labels = pd.get_dummies(X['y']).astype(int).as_matrix()

train_data = np.matrix(fvecs).astype(np.float32)
train_labels = np.array(labels).astype(dtype=np.float32)

#==============================================================================
# Initialize testing dataset
#==============================================================================
Xt, yt = datasets.make_moons(1000, noise=0.20)
Xt = pd.DataFrame(Xt, columns = ['x0', 'x1'])
Xt['y'] = yt

fvecst = Xt[['x0', 'x1']].astype(float).as_matrix()
labelst = pd.get_dummies(Xt['y']).astype(int).as_matrix()

test_data = np.matrix(fvecst).astype(np.float32)
test_labels = np.array(labelst).astype(dtype=np.float32)

#==============================================================================
# Weight initialization functions
# Includes 'zeroes', 'uniform', and 'xavier' methods
#==============================================================================
# Init weights Xavier method
def xavier(shape):
    (fan_in, fan_out) = shape
    low = -4*np.sqrt(6.0/(fan_in + fan_out)) # {sigmoid:4, tanh:1} 
    high = 4*np.sqrt(6.0/(fan_in + fan_out))
    return tf.Variable(tf.random_uniform(shape, minval=low, maxval=high, dtype=tf.float32))

x = tf.placeholder("float", shape=[None, num_features]) # Empty nodes to be fed feature set
y_ = tf.placeholder("float", shape=[None, num_labels])  # Empty nodes to be fed label set

test_data_node = tf.constant(test_data)

#w_hidden = tf.Variable(tf.zeros(shape, dtype=tf.float32))                      # Init hidden weights 'zeroes' method
#w_hidden = tf.Variable(tf.random_normal(shape, stddev=0.01, dtype=tf.float32)) # Init hidden weights 'uniform' method
w_hidden = xavier([num_features, num_hidden])                                   # Init hidden weights 'xavier' method
b_hidden = tf.Variable(tf.zeros([1, num_hidden], dtype=tf.float32))             # Init hidden biases 'zeroes' method
hidden = tf.nn.tanh(tf.matmul(x,w_hidden) + b_hidden)                           # Hidden layer

w_out = xavier([num_hidden, num_labels])                                        # Init output weights 'xavier' method
b_out = tf.Variable(tf.zeros([1, num_labels], dtype=tf.float32))                # Init output biases 'zeroes' method

y = tf.nn.softmax(tf.matmul(hidden, w_out) + b_out)                             # Output layer with softmax activations
cross_entropy = -tf.reduce_sum(y_*tf.log(y))                                    # Optimization
train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)    # Optimization

predicted_class = tf.argmax(y,1)                                           
correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))

#==============================================================================
# Run it run it run it!
#==============================================================================
with tf.Session() as s:
    tf.initialize_all_variables().run()
    
    for step in range(num_epochs * train_size // batch_size):
        offset = (step * batch_size) % train_size
        batch_data = train_data[offset:(offset + batch_size), :]
        batch_labels = train_labels[offset:(offset + batch_size)]
        train_step.run(feed_dict={x: batch_data, y_: batch_labels})
        print("Accuracy:", accuracy.eval(feed_dict={x: test_data, y_: test_labels}))
    
    eval_fun = lambda X: predicted_class.eval(feed_dict={x:X})
    plot(test_data, test_labels, eval_fun)
                                            