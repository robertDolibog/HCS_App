# MixedClassifier.py

import os
import re

from Services.ClassifierInterface import ClassifierInterface
from Services.FilenameClassifier import FilenameClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from Services.Helpers.ExtractTextFromFiles import ExtractTextFromFiles


class MixedClassifier(ClassifierInterface):
    def __init__(self,
                 filename_config=os.path.join(os.path.dirname(__file__), "sensitivity_keywords.json")):
        # Filename‐based sub‐classifier
        self.name_classifier = FilenameClassifier(config_path=filename_config)

        # Keywords for content scoring
        self.sensitive_keywords = [
            "confidential", "password", "ssn", "iban", "secret", "tax",
            "salary", "diagnosis", "medical", "invoice", "identity",
            "passport", "contract"
        ]

        # Build a TF vectorizer over those keywords (no IDF)
        self.vectorizer = TfidfVectorizer(
            vocabulary=self.sensitive_keywords,
            use_idf=False,
            norm=None
        )
        # **Fit on a dummy document** so transform() won’t complain
        self.vectorizer.fit([" ".join(self.sensitive_keywords)])

    


    def preprocess(self, text: str) -> str:
        """
        Lowercase + regex‐tokenize on words,
        removing any non‐word chars.
        """
        tokens = re.findall(r"\b\w+\b", text.lower())
        return " ".join(tokens)

    def content_score(self, filepath: str) -> float:
        """Sum of term‐frequencies for sensitive keywords."""
        raw = ExtractTextFromFiles.extract_text(filepath)
        processed = self.preprocess(raw)
        vec = self.vectorizer.transform([processed])
        return vec.sum()

    def classify(self, filepath: str) -> str:
        # 1) Filename‐based
        name_pred = self.name_classifier.classify(filepath).upper()
        # 2) Content‐based
        content_pred = "SENSITIVE" if self.content_score(filepath) > 0.2 else "INSENSITIVE"

        # If either flags sensitive, it's sensitive
        return "SENSITIVE" if (name_pred == "SENSITIVE" or content_pred == "SENSITIVE") else "INSENSITIVE"
