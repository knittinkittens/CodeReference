#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 11:08:47 2017

"""
#==============================================================================
# Package imports
#==============================================================================
import pandas as pd
import pymssql
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import MDS

#==============================================================================
# Connect to database and select columns we want
#==============================================================================


#==============================================================================
# Data preprocessing
#==============================================================================
df         = df[~df['text'].isnull()]                                           # Get rid of null rows (responses that have no comment)
df['text'] = df['text'].str.lower()                                             # Convert all text to lowercase
df['text'] = df['text'].apply(lambda x: re.sub(r'[^a-zA-Z\s:]', '', x) )        # Get rid of all special characters and numbers
df['text'] = df['text'].apply(lambda x: re.sub(r'farmers|insurance', '', x) )   # Get rid of all words that mean nothing
df['text'] = df['text'].apply(lambda x: nltk.word_tokenize(x))                  # Tokenize responses into lists of words

# Get rid of stopwords
filtered_words = lambda x: [word for word in re.sub("[^\w]", " ",  str(x)).split() if word not in set(nltk.corpus.stopwords.words('english'))]
df['text']     = df['text'].apply(filtered_words)

corpus     = [val for sublist in list(df['text']) for val in sublist]       # Get a list of all words, including repetition
set_corpus = list(set(corpus))                                              # Get a unique list of all words

# Get a column of string representation of the responses converted to their stems
stemmed       = [[nltk.stem.snowball.SnowballStemmer("english").stem(t) for t in words] for words in df.text.values]
df['stemmed'] = stemmed

#df = df.head(10000)
# Get a stem-to-original dictionary for the most likely re-translation of the stem to the original word
vocab_list = [[t, nltk.stem.snowball.SnowballStemmer("english").stem(t)] for t in corpus] 
vocab_list = pd.DataFrame(vocab_list, columns = ['orig', 'stem'])
vocab_list = vocab_list.groupby(['orig', 'stem']).size().reset_index()
vocab_list = vocab_list[vocab_list.groupby(['stem'])[0].transform(max) == vocab_list[0]]

# Replace stems with their actual words
df['stemmed'] = [[ list(vocab_list['orig'][vocab_list['stem'] == t])[0] if t in vocab_list['stem'].values else t for t in words ] for words in df.stemmed.values]
df['stemmed'] = df['stemmed'].apply(lambda x: ' '.join(x))
df = df[df['ltr'] <=6 ]
#==============================================================================
# TF=IDF Matrix 
#==============================================================================
tfidf_vectorizer = TfidfVectorizer(max_df=0.7, max_features=200000, min_df=0.001, use_idf=True, tokenizer=None, ngram_range=(1,3))
tfidf_matrix     = tfidf_vectorizer.fit_transform(df['stemmed'])
terms            = tfidf_vectorizer.get_feature_names()

dist = 1 - cosine_similarity(tfidf_matrix)

#==============================================================================
# K-Means Clustering
#==============================================================================
num_clusters = 15
km = KMeans(n_clusters=num_clusters)
km.fit(tfidf_matrix)

clusters = km.labels_.tolist()

df['cluster'] = clusters
df['cluster'].value_counts()

grouped = df['ltr'].groupby(df['cluster'])

order_centroids = km.cluster_centers_.argsort()[:, ::-1] 
for i in range(num_clusters):
    for ind in order_centroids[i, :10]: 
        print(' %s' % terms[ind].split(' '), end=',')
    print('\n')

#==============================================================================
# Multidimensional Scaling for Visualization
#==============================================================================å
MDS()
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1, n_jobs = 4)
pos = mds.fit_transform(dist)  
xs, ys = pos[:, 0], pos[:, 1]
