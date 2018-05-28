from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pandas as pd
import numpy as np
import tensorflow as tf
import keras
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
import cPickle as pickle


dictionary = open("/Users/neil/workplace/stemmed_dictionary.txt").read().lower()


## load tfidf model
tfidf = pickle.load(open('/Users/neil/workplace/tfidf.pk', "rb"))

## load NN model
model = keras.models.load_model("/Users/neil/workplace/model.h5")
#model = model_from_json(json_string)
#model.load_weights('my_model_weights.h5')


#lookup the filename
with open("/Users/neil/workplace/all_filenames.txt") as f:
    filenames = f.readlines()

filenames = [file.strip() for file in filenames]
lookup = {}
for filename in filenames:
    base = filename.split(".")[0]
    if base in lookup.keys():
        raise NameError('base of filename is a duplicate')
    lookup[base] = filename

clean_files = os.listdir("/Users/neil/workplace/clean_files/")
for doc in clean_files:
    base = doc.split(".")[0]
    original_file = lookup[base]
    ## transform doc into tfidf matrix
    data = tfidf.transform(doc).todense()
    tfidf_cols = tfidf.get_feature_names()
    df = pd.DataFrame(data, columns=tfidf_cols)
    #predict class of document
    y_pred = model.predict_classes(df)
    if y_pred == 0:
        old = "/Users/neil/workplace/raw_files/" + str(original_file)
        new = "/Users/neil/workplace/model_output/irrelevant/" +  str(original_file)
        os.rename(old,new)
    elif y_pred == 1:
        old = "/Users/neil/workplace/raw_files/" + str(original_file)
        new = "/Users/neil/workplace/model_output/relevant_inappropriate/" + str(original_file)
        os.rename(old,new)

    #based on class, mv to correct folder
