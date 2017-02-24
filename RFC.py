# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:48:55 2016

"""

from sklearn.ensemble import RandomForestClassifier 
from sklearn.grid_search import RandomizedSearchCV
from random import randint
from sklearn import metrics

#==============================================================================
# Random Forest Classifier
#==============================================================================
def rfc_model(X_train, X_test, y_train, y_test):

    #Set range of parameters to test using Randomized Search
    n_trees = range(50, 1000)
    max_feats = ['auto', None]
    seed = randint(5, 500)
    
    # Find best parameters for model    
    param_dist = dict(
                      n_estimators = n_trees
                    , max_features = max_feats
                )
            
    model= RandomForestClassifier()
    
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
    best_trees = rand.best_params_['n_estimators']
    best_features = rand.best_params_['max_features']

    # Execute best model and return the testing sccores
    forest = RandomForestClassifier(            
                      n_estimators = best_trees
                    , max_features = best_features
                )
                    
    forest = forest.fit(X_train,y_train)
    expected = y_test
    predicted = forest.predict(X_test)
    accuracy = metrics.accuracy_score(expected, predicted)
    class_report = metrics.classification_report(expected, predicted)
    confus_mat = metrics.confusion_matrix(expected, predicted)
    
    return accuracy, class_report, confus_mat