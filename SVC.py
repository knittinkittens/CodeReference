# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:46:59 2016

"""

from sklearn.svm import SVC
from sklearn.grid_search import RandomizedSearchCV
from random import randint
from sklearn import metrics

#==============================================================================
# Support Vector Classifier
#==============================================================================
def svc_model(X_train, X_test, y_train, y_test):
    
    # Set range of parameters to test using Randomized Search
    c_range = range(1, 50)
   # g_range = [0.0001, 0.001, 0.01, 1, 10]
    seed = randint(5, 500)
    
    # Find best parameters for model
    param_dist = dict(
                    C=c_range
                    #,gamma = g_range
                )
                
    model= SVC(kernel = 'rbf')
    
    rand = RandomizedSearchCV(
                      model
                    , param_dist
                    , cv = 10
                    , scoring = 'accuracy'
                    , n_iter = 10
                    , random_state = seed
                )
                
    rand.fit(X_train, y_train)

    # Assign best parameters for model
    best_c = rand.best_params_['C']
    #best_gamma = rand.best_params_['g_range']    
    
    # Execute best model and return the testing sccores
    model = SVC(
                  C = best_c
                , kernel = 'rbf'
                # , gamma = best_gamma
            )
            
    model.fit(X_train, y_train)
    expected = y_test
    predicted = model.predict(X_test)
    accuracy = metrics.accuracy_score(expected, predicted)
    class_report = metrics.classification_report(expected, predicted)
    confus_mat = metrics.confusion_matrix(expected, predicted)    

    
    return accuracy, class_report, confus_mat