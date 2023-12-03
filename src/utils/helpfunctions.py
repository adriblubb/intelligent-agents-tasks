import src.utils.wikipedia as wiki
import src.utils.functions as functions
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import *
from nltk.stem.porter import *
import numpy as np
from collections import Counter


# Download necessary wiki-articles and store in cache
def download_wiki():
    # Create directory with class wikipedia
    wikit = wiki.Wikipedia()
    # Download corpus list
    content = functions.read_file("/home/user/src/exercise1/data/corpus.txt")
    content = content.split("\n")
    # [1:] because first object is empty
    for c in content[1:]:
        wikit.get(c)
    # Download sell list
    content = functions.read_file("/home/user/src/exercise1/data/sell.txt")
    content = content.split("\n")
    # [1:] because first object is empty
    for c in content[1:]:
        wikit.get(c)


# Preprocess text into tokens after specific procedure
def preprocessing(text):
    # Make text to tokens and remove punctuation with regex-pattern: w for word-char, + for many w
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)

    # Convert to lowercase and filter out all tokens that are non-alphabetic
    cleared_token = [token.lower() for token in tokens if token.isalpha()]

    # Filter out stop words
    filtered_token = [token for token in cleared_token if token not in stopwords.words('english')]

    # Stem tokens
    stemmer = PorterStemmer()
    processed_token = [stemmer.stem(token) for token in filtered_token]
    return processed_token


# Calculate the frequency of the words over the whole corpus
def calc_freq(database, corpus_list):
    doc_f = {}
    for title in corpus_list:
        tokens = database[title]
        # For all words in document add title
        for token in np.unique(tokens):
            try:
                doc_f[token].add(title)
            except KeyError:
                doc_f[token] = {title}
    # Calculate the frequency over number of title in which the word appears
    for key in doc_f:
        doc_f[key] = len(doc_f[key])
    return doc_f


# Return the frequency or one to prevent division by 0
def doc_freq(token, doc_f):
    try:
        i = doc_f[token]
    # If word doesn't exist return one
    except KeyError:
        i = 1
    return i


# Calculate the tf_idf over the corpus (inclusive the document to sell)
def calc_tf_idf(database, corpus_list):
    tf_idf = {}
    # Calculate the document frequency over the corpus
    doc_f = calc_freq(database, corpus_list)
    for title in corpus_list:
        tokens = database[title]
        # Count number of words in the document
        counter = Counter(tokens)
        # Document length
        words_count = len(tokens)
        # Calculate tf_idf
        for token in np.unique(tokens):
            # Calculate term_frequency
            tf = counter[token] / words_count
            # Get document_frequency for a specific token
            df = doc_freq(token, doc_f)
            # Calculate idf
            idf = np.log(len(corpus_list) / df)
            # Calculate the tf_idf and store them with (title, token) key
            tf_idf[title, token] = tf * idf
    return tf_idf


# Valuating the tf_idf on a given query as list of documents and the selling document
def valuating(database, query, tf_idf_docs, sell_doc_title):
    value_query = []
    for que in query:
        query_weights = {}
        tokens = database[que]
        # Calculate the value for a document based on a specific query
        for key in tf_idf_docs:
            # Only those are relevant which are in the query
            if key[1] in tokens:
                try:
                    query_weights[key[0]] += tf_idf_docs[key]
                except KeyError:
                    query_weights[key[0]] = tf_idf_docs[key]

        # Sort the values in descending order
        sorted_arr = sorted([query_weights[key] for key in query_weights], reverse=True)
        # Calculate the mean over the tf_idf of document without the highest value (usually the doc from the query)
        mean = np.mean(sorted_arr[1:])

        value_query.append((mean < query_weights[sell_doc_title], query_weights[sell_doc_title] - mean))

    # Calculate value for the selling document based on the query
    value = 0
    # Scale the value based on the individual outputs from the query
    scale_factor = 0
    for val in value_query:
        if val[0]:
            scale_factor += 1
            value += val[1]
    return value * scale_factor/3


# Calculate price for the value, has the possibility to increase his price based on the opponent
def get_price_for_value(value, factor_oppo=1):
    return round(value**(1/100) * 5, 4) * factor_oppo


# Calculate relation of docA through docB
def get_percentage(score_docA, score_docB):

    percentage = score_docA / score_docB

    # maybe handler for correct inputs eg minus etc. possibly won't happen with tfidf
    return percentage
