
import os
import re
import string
import joblib

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

from PyPDF2 import PdfReader
import docx

from .ClassifierInterface import ClassifierInterface
from ..Helpers.ExtractTextFromFiles import ExtractTextFromFiles


# Ensure the same NLTK models are available at runtime
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

class ModelClassifier(ClassifierInterface):
    def __init__(self, model_path: str = None):

        # If none given, assume it's in the same folder
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "Helpers",
                                      'sensitivity_detector.joblib')

        # Load the trained sklearn Pipeline (TF-IDF + classifier)
        self.pipeline = joblib.load(model_path)

        # Prep for preprocessing
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))



    def _preprocess(self, text: str) -> str:
        # 1) lowercase + strip + remove HTML tags
        text = text.lower().strip()
        text = re.sub(r"<.*?>", "", text)
        # 2) remove punctuation
        text = re.sub(r"[{}]".format(re.escape(string.punctuation)), " ", text)
        # 3) collapse whitespace
        text = re.sub(r"\s+", " ", text)
        # 4) remove numeric references ([12], etc.)
        text = re.sub(r"\[[0-9]*\]", " ", text)
        # 5) remove any non-word/non-space
        text = re.sub(r"[^\w\s]", "", text)
        # 6) remove digits
        text = re.sub(r"\d", " ", text)
        # final whitespace cleanup
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _remove_stopwords(self, text: str) -> str:
        return " ".join(w for w in text.split() if w not in self.stop_words)

    def _get_wordnet_pos(self, tag: str):
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

    def _lemmatize(self, text: str) -> str:
        tokens = word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        lemmas = [
            self.lemmatizer.lemmatize(tok, self._get_wordnet_pos(tag))
            for tok, tag in pos_tags
        ]
        return " ".join(lemmas)

    def _final_preprocess(self, text: str) -> str:
        t1 = self._preprocess(text)
        t2 = self._remove_stopwords(t1)
        t3 = self._lemmatize(t2)
        return t3

    def classify(self, file_path: str) -> str:
        """
        Returns "SENSITIVE" or "INSENSITIVE" by:
          1. Extracting text
          2. Applying the same preprocessing pipeline
          3. Running the pretrained sklearn pipeline
        """
        raw = ExtractTextFromFiles.extract_text(file_path)
        if not raw:
            # If we can't read it, default to INSENSITIVE (or choose as you wish)
            return "INSENSITIVE"

        cleaned = self._final_preprocess(raw)
        pred = self.pipeline.predict([cleaned])[0]
        return pred