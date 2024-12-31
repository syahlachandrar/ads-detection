# tf_idf.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from rake_nltk import Rake
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize

# Unduh stopwords jika belum
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# TF-IDF Extraction
def extract_top_keywords_tfidf(captions, top_n=5):
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('indonesian'))
    tfidf_matrix = vectorizer.fit_transform(captions)
    features = vectorizer.get_feature_names_out()
    
    keywords = []
    for row in tfidf_matrix:
        scores = row.toarray().flatten()
        top_indices = scores.argsort()[-top_n:]  # Ambil top N
        top_features = [features[idx] for idx in top_indices]
        keywords.append(top_features)
    return keywords

# RAKE Extraction
def extract_top_keywords_rake(captions, top_n=2):
    rake_nltk_var = Rake(stopwords=stopwords.words('indonesian'))
    keywords = []
    for caption in captions:
        rake_nltk_var.extract_keywords_from_text(caption)
        keywords.append(rake_nltk_var.get_ranked_phrases()[:top_n])  # Mengembalikan list of lists
    return keywords  # Ini bisa jadi list of list, jadi Anda perlu mengubahnya jadi string

