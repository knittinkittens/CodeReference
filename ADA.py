# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:51:16 2016

"""

from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.grid_search import RandomizedSearchCV
from random import randint
from sklearn import metrics

#==============================================================================
# AdaBoost Classifier
#==============================================================================
def adaboost_model(X_train, X_test, y_train, y_test):
    
     #Set range of parameters to test     
    t_algorithm = ['SAMME.R', 'SAMME']
    t_n_estimators = range(50, 1000)
    t_base_estimator__max_features = ['auto', None]
    t_base_estimator__splitter = ['best', 'random']
    seed = randint(5, 500)
    
    # Find best parameters for model by running Randomized Search on them
    param_dist = dict(
                      algorithm = t_algorithm
                    , n_estimators = t_n_estimators
                    , base_estimator__max_features = t_base_estimator__max_features
                    , base_estimator__splitter = t_base_estimator__splitter
                )
                
    model= AdaBoostClassifier(base_estimator = DecisionTreeClassifier())
    
    rand = RandomizedSearchCV(
                      model
                    , param_dist
                    , cv = 10
                    , scoring = 'accuracy'
                    , n_iter = 15
                    , random_state = seed
                )
                
    rand.fit(X_train, y_train)
    
    # Assign best parameters for model
    best_algorithm = rand.best_params_['algorithm']
    best_n = rand.best_params_['n_estimators']
    best_features = rand.best_params_['base_estimator__max_features']
    best_splitter = rand.best_params_['base_estimator__splitter']
    
    # Execute best model and return the testing sccores     
    bdt = AdaBoostClassifier(
                      base_estimator = DecisionTreeClassifier(max_features = best_features, splitter = best_splitter)
                    , algorithm = best_algorithm
                    , n_estimators = best_n
                )
    
    bdt.fit(X_train, y_train)
    expected = y_test
    predicted = bdt.predict(X_test)
    accuracy = metrics.accuracy_score(expected, predicted)
    class_report = metrics.classification_report(expected, predicted)
    confus_mat = metrics.confusion_matrix(expected, predicted)
        
    return accuracy, class_report, confus_mat