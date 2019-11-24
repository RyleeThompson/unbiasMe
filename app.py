from flask import Flask, render_template, request
import helpers
import pickle
import os
import time
import pandas as pd
import numpy as np
import nltk
import platform


# Web app
app = Flask(__name__)

#init
DEFAULT_PATH = os.getcwd()

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
cat_dict, stem_dict, counts_dict = helpers.load_LIWC_dictionaries()
loaded_model = pickle.load(open(os.path.join(DEFAULT_PATH, 'resources', 'NB_Subj_Model.sav'), 'rb'), encoding = 'latin1')
count_vect = pickle.load(open(os.path.join(DEFAULT_PATH, 'resources', 'count_vect.sav'), 'rb'), encoding = 'latin1')
tfidf_transformer = pickle.load(open(os.path.join(DEFAULT_PATH, 'resources', 'tfidf_transformer.sav'), 'rb'), encoding = 'latin1')
bias, assertives, factives, hedges, implicatives, report_verbs, positive_op, negative_op, wneg, wpos, wneu, sneg, spos, sneu = helpers.load_acl13_lexicons()

print(platform.python_version())

model = pickle.load(open('defaultRF.sav', 'rb'))

def convertUrlsToFeatures(urls):
    features = []
    for url in urls:
        result = helpers.scrape(url)
        print(result[1])
        features.append(helpers.start(result[0], result[1], result[2], cat_dict, stem_dict, counts_dict, loaded_model, count_vect, tfidf_transformer, bias, assertives,
                                      factives, hedges, implicatives, report_verbs, positive_op, negative_op, wneg, wpos, wneu, sneg, spos, sneu))
    features = np.array(features)
    return features

def putItInDaModel(features):
    preds = model.predict_proba(features)[:, 1]
    ix = np.argsort(preds)
    preds = preds[ix]
    return ix, preds

def sortTheGoods(ix, urls, titles, snippets):
    urls = np.array(urls)[ix][::-1]
    titles = np.array(titles)[ix][::-1]
    snippets = np.array(snippets)[ix][::-1]
    return urls, titles, snippets
        

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    render_template("results.html")
    x = request.args.get('search')
    searchResults = helpers.getSearchResults(x, 2)
    urls, titles, snippets = helpers.getInfo(searchResults)
    #urls = ["https://www.cnn.com/2019/11/22/politics/nunes-vienna-trip-ukrainian-prosecutor-biden/index.html", "https://www.theguardian.com/us-news/2019/nov/23/trump-impeachment-released-documents-reveal-giuliani-pompeo-links", "https://www.bbc.com/news/world-us-canada-39945744"]
    features = convertUrlsToFeatures(urls)
    ix, preds = putItInDaModel(features)
    urls, titles, snippets = sortTheGoods(ix, urls, titles, snippets)
    preds = preds[::-1]*100
    print(urls)
    print(preds)
    results = np.c_[titles, urls]
    results = np.c_[results, snippets]
    results = np.c_[results, preds]
    print(results)
    return render_template("results.html", info = results)
    
#starttimer = time.time()
#results = helpers.getSearchResults("trump impeachment", 2)
#urls, titles, snippets = helpers.getInfo(results)
#features = convertUrlsToFeatures(urls)
#ix, preds = putItInDaModel(features)
#urls, titles, snippets = sortTheGoods(ix, urls, titles, snippets)
#helpers.start(x[0], x[1], x[2], cat_dict, stem_dict, counts_dict, loaded_model, count_vect, tfidf_transformer, bias, assertives, factives, hedges, implicatives, report_verbs, positive_op, negative_op, wneg, wpos, wneu, sneg, spos, sneu)
#endttimer = time.time()
#print(endttimer - starttimer)
