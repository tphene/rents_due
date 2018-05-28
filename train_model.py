from nltk.stem import LancasterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pandas as pd
import numpy as np
import re
import cPickle as pickle
from sklearn.cross_validation import train_test_split
import tensorflow as tf
import keras
from keras.activations import softmax
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier


## Load Dictionary
dictionary = open("/Users/neil/Documents/Mary/dictionary.txt").read().lower()
dictionary = dictionary.split(" . ")
len(dictionary)

# Stem all words in the dictionary
stemmer = LancasterStemmer()
dictionary = [stemmer.stem(word).strip() for word in dictionary]
dictionary = set(dictionary)


# remove all characters that arent alphanumeric
def clean_doc(doc):
    clean_doc = ''
    for char in doc:
        #if ((65<=ord(char)<=90) | (97<=ord(char)<=122)):
        if ((48<=ord(char)<=57) | (65<=ord(char)<=90) | (97<=ord(char)<=122)):
            clean_doc = clean_doc + char
        elif (ord(char) == 39) | (ord(char) == 45):
            continue
        else:
            char = " "
            clean_doc = clean_doc + char
    clean_doc = re.sub(" +", " ", clean_doc)
    clean_doc = clean_doc.lower()
    return clean_doc

#Function to stem all words in a document
def stem_docs(df):
    docs = []
    for enum,doc in enumerate(list(df['text'])):
        if enum % 1000 == 0:
            print(enum)
        doc = clean_doc(str(doc))
        doc = doc.split(" ")
        doc = [stemmer.stem(word).strip() for word in doc]
        doc = " ".join(doc)
        docs.append(doc)
    df = pd.DataFrame(docs,columns=['text'])
    return df

#def lemmatize_docs(df):
#    docs = []
#    for enum,doc in enumerate(list(df['text'])):
#        if enum % 1000 == 0:
#            print(enum)
#        doc = clean_doc(str(doc))
#        doc = doc.split(" ")
#        doc = [stemmer.stem(word).strip() for word in doc]
#        doc = " ".join(doc)
#        docs.append(doc)
#    df = pd.DataFrame(docs,columns=['text'])
#    return df


## Load Relevant CSVs
files = os.listdir("/Users/neil/Documents/Mary/relevant_filenames/")
try:
    files.remove(".DS_Store")
except:
    pass

for enum,f in enumerate(files):
    filepath = "/Users/neil/Documents/Mary/relevant_filenames/" + str(f)
    if enum == 0:
        relevant = pd.read_csv(filepath)
        relevant = relevant[['text']]
    else:
        temp = pd.read_csv(filepath)
        temp = temp[['text']]
        relevant = relevant.append(temp)
relevant.reset_index(inplace=True)
relevant.drop(['index'], axis=1, inplace=True)


## Load Irrelevant CSVs
files = os.listdir("/Users/neil/Documents/Mary/irrelevant_filenames/")
try:
    files.remove(".DS_Store")
except:
    pass

for enum,f in enumerate(files):
    filepath = "/Users/neil/Documents/Mary/irrelevant_filenames/" + str(f)
    if enum == 0:
        irrelevant = pd.read_csv(filepath)
        irrelevant = irrelevant[['text']]
    else:
        temp = pd.read_csv(filepath)
        temp = temp[['text']]
        irrelevant = irrelevant.append(temp)
irrelevant.reset_index(inplace=True)
irrelevant.drop(['index'], axis=1, inplace=True)

## stem the relevant and irrelevant dfs
relevant = stem_docs(relevant)
irrelevant = stem_docs(irrelevant)

## append labels, combine the dfs,
relevant['target_val'] = [1]*len(relevant)
irrelevant['target_val'] = [0]*len(irrelevant)
df = relevant.append(irrelevant).dropna()
df.dropna(inplace=True)
df.reset_index(inplace=True)
# randomize the df
df = df.sample(frac=1)


## Get TFIDF DF
def get_tfidf(corpus, dictionary):
    tfidf = TfidfVectorizer(ngram_range=(1,5), vocabulary=dictionary, lowercase=True)
    tfidf = tfidf.fit(corpus)
    with open('/Users/neil/workplace/tfidf.pk', 'wb') as f:
        pickle.dump(tfidf, f)
    data = tfidf.transform(corpus).todense()
    tfidf_cols = tfidf.get_feature_names()
    df = pd.DataFrame(data, columns=tfidf_cols)
    return tfidf, df

tfidf_model, tfidf_df = get_tfidf(list(df.text), dictionary)
tfidf_df['target_val'] = list(df.target_val)


## Find all rows that have all 0 values
indexes = []
for idx, row in zip(tfidf_df.drop(['target_val'],axis=1).loc[:].index, tfidf_df.drop(['target_val'],axis=1).loc[:].values):
    if all(row == [0] * len(row)):
        indexes.append(idx)

## Hard code a zero label to rows that have all zero values
for idx in indexes:
    tfidf_df.loc[idx, 'target_val'] = 0


## split the df into chunks of 100,000
for num in range(int(np.ceil(len(tfidf_df)/100000.0))):
    f = '/Users/neil/Documents/Mary/tfidf/tfidf' + str(num) + ".csv"
    start = num*100000
    end = (num+1)*100000
    tfidf_df[start:end].to_csv(f)



def generator(path):
    while 1:
        df = pd.read_csv(path).reset_index().drop(['index','Unnamed: 0','Unnamed: 1'], axis=1)
        x_train = df.drop(['target_val'],axis=1).values
        y_train = df.target_val.values
        y_train = np_utils.to_categorical(y_train, 2)
        for x,y in zip(x_train, y_train):
            yield (x_train, y_train)
        f.close()


def nn(dictionary):
    model = Sequential()
    model.add(Dense(5000, input_dim=len(dictionary)-1, activation='relu'))
    model.add(Dense(2500, activation='relu'))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    files = os.listdir("/Users/neil/Documents/Mary/tfidf/")
    files.remove("tfidf0.csv")
    try:
        files.remove(".DS_Store")
    except:
        pass
    for f in files:
        path = "/Users/neil/Documents/Mary/tfidf/" + str(f)
        model.fit_generator(generator(path), steps_per_epoch=2, nb_epoch=2, verbose=1)

    tfidf_df = pd.read_csv("/Users/neil/Documents/Mary/tfidf/tfidf0.csv").reset_index().drop(['index','Unnamed: 0','Unnamed: 1'], axis=1)
    x_test = tfidf_df.drop(['target_val'],axis=1).values
    y_test = tfidf_df.target_val.values
    y_test = np_utils.to_categorical(y_test, 2)
    score = model.evaluate(x_test, y_test, verbose=1)
    print("Test Score:", score)
    return model


model = nn(dictionary)

#model.save("Users/neil/workplace/model.h5")
model.save_weights("Users/neil/workplace/weights.h5")
model.save_json("Users/neil/workplace/json.h5")
