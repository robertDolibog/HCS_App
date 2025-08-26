import os
import csv
import re
import string
import nltk

import pandas as pd

# Text preprocessing\import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

# Model building & evaluation
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    classification_report,
    f1_score,
    accuracy_score,
    confusion_matrix,
    roc_curve,
    auc
)
from sklearn.feature_extraction.text import TfidfVectorizer



# Model Pipeline
from sklearn.pipeline import Pipeline


# Save trained Pipeline
import joblib



# Optional: plotting ROC curves
import matplotlib.pyplot as plt

# File parsing
from PyPDF2 import PdfReader
import docx

# Download NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
nltk.download('stopwords')

# ======== USER CONFIG ========
dataset_dir = "TestData"
ground_truth_path = os.path.join(dataset_dir, "ground_truth.csv")
sensitive_dir = os.path.join(dataset_dir, "sensitive")
insensitive_dir = os.path.join(dataset_dir, "insensitive")
# ==============================

# === Load ground truth ===
truth = {}
with open(ground_truth_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        truth[row["filename"]] = row["sensitivity"]

# === Helper: extract plain text ===
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".txt":
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(path)
            return " ".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".docx":
            doc = docx.Document(path)
            return " ".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return ""
    return ""

# === Text Pre-processing ===
# 1. Lowercase, strip, remove HTML tags, punctuations, digits

def preprocess(text):
    text = text.lower()
    text = text.strip()
    text = re.compile(r'<.*?>').sub('', text)
    text = re.compile(r'[%s]' % re.escape(string.punctuation)).sub(' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# 2. Stopword removal
def remove_stopwords(text):
    words = [w for w in text.split() if w not in stopwords.words('english')]
    return ' '.join(words)

# 3. Lemmatization
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

# Tokenize, POS-tag, and lemmatize
def lemmatize_text(text):
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    lemmas = [lemmatizer.lemmatize(tok, get_wordnet_pos(tag)) for tok, tag in pos_tags]
    return ' '.join(lemmas)

# 4. Final preprocessing pipeline
def final_preprocess(text):
    step1 = preprocess(text)
    step2 = remove_stopwords(step1)
    step3 = lemmatize_text(step2)
    return step3

# === Read files and build DataFrame ===
data = []
for folder in (sensitive_dir, insensitive_dir):
    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if not os.path.isfile(full_path):
            continue
        label = truth.get(filename)
        if label is None:
            continue
        raw = extract_text(full_path)
        if raw:
            data.append((raw, label.upper()))


df = pd.DataFrame(data, columns=["text", "label"])

# Apply final preprocessing
df["cleaned_text"] = df["text"].apply(final_preprocess)

# === Train/Test Split ===
X = df["cleaned_text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# === Vectorization ===
tfidf_vect = TfidfVectorizer(max_df=0.9, min_df=5, ngram_range=(1,2))
X_train_tfidf = tfidf_vect.fit_transform(X_train)
X_test_tfidf  = tfidf_vect.transform(X_test)




# 1. Create a Pipeline
pipeline = Pipeline([
    ('vect', TfidfVectorizer(max_df=0.9, min_df=5, ngram_range=(1,2))),
    ('clf', LogisticRegression(max_iter=1000, random_state=42))
])

# 2. Fit on training data
pipeline.fit(X_train, y_train)


# Dump to file
joblib.dump(pipeline, 'sensitivity_detector.joblib')
