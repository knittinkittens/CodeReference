# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:50:00 2016

"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.grid_search import RandomizedSearchCV
from random import randint
from sklearn import metrics

#==============================================================================
# K-Neighbors Classifier
#==============================================================================
def knn_model(X_train, X_test, y_train, y_test):
    
    #Set range of parameters to test using Randomized Search 
    k_range = range(1, 50)
    weight_options = ['uniform', 'distance']
    seed = randint(5, 500)    
    
    # Find best parameters for model    
    param_dist = dict(
                n_neighbors = k_range
                , weights = weight_options
            )
            
    knn = KNeighborsClassifier(n_jobs = 2)
    
    rand = RandomizedSearchCV(
                      knn
                    , param_dist
                    , cv = 10
                    , scoring = 'accuracy'
                    , n_iter = 15
                    , random_state = seed
                )
                
    rand.fit(X_train, y_train)
    
    # Assign best parameters for model
    k_neighbors = rand.best_params_['n_neighbors']
    k_weights = rand.best_params_['weights']

    # Execute best model and return the testing sccores    
    knn = KNeighborsClassifier(
                      n_neighbors = k_neighbors
                    , weights = k_weights
                )
                
    knn.fit(X_train, y_train) 
    expected = y_test
    predicted = knn.predict(X_test)
    accuracy = metrics.accuracy_score(expected, predicted)
    class_report = metrics.classification_report(expected, predicted)
    confus_mat = metrics.confusion_matrix(expected, predicted)
    
    return accuracy, class_report, confus_mat
