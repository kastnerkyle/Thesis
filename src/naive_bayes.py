#!/usr/bin/env python

import glob
import numpy as np
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split


def get_acl_imdb_text(froot, vec):
    sets = ['train', 'test']
    lookup = {'pos': 1,
              'neg': 0}
    folders = lookup.keys()
    all_text = []
    all_labels = []
    for s in sets:
        for folder in folders:
            fs = glob.glob(froot + '/' + s + '/' + folder + '/*.txt')
            for fname in fs:
                print "Processing: " + fname
                with open(fname, 'r') as f:
                    all_text.append(f.read())
                    all_labels.append(lookup[folder])

    return vec.fit_transform(all_text), np.array(all_labels)

froot = '../data/sentiment_analysis/aclImdb'
text_vec = TfidfVectorizer(sublinear_tf=True, max_df=0.5, stop_words='english')
X, y = get_acl_imdb_text(froot, text_vec)
X_tr, X_tst, y_tr, y_tst = train_test_split(X, y,
                                            train_size=.8, random_state=55)


def fit_model(bayes, X_tr=X_tr, X_tst=X_tst, y_tr=y_tr, y_tst=y_tst):
    bayes.fit(X_tr, y_tr)
    yhat = bayes.predict(X_tst)
    return (np.abs(yhat - y_tst)).mean()

print "Bernoulli Misclass: ", fit_model(BernoulliNB())
print "Multinomial Misclass: ", fit_model(MultinomialNB())
