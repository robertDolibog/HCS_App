import os
import json
import re

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
)
from .ClassifierInterface import ClassifierInterface
from ..Helpers.ExtractTextFromFiles import ExtractTextFromFiles
from .Recognizers.PrivacyKeywordRecognizer import PrivacyKeywordRecognizer
from presidio_analyzer import EntityRecognizer
from nltk.corpus import wordnet




class PresidioClassifier(ClassifierInterface):
    def __init__(self,
                 config_path: str = None,
                 min_score: float = 0.2):
        # Load config
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "sensitivity_keywords.json"
            )
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        # 1) extension‐based
        self.sensitive_exts = {
            ext if ext.startswith('.') else f".{ext}"
            for ext in cfg.get("sensitive_extensions", [])
        }

        # 2) prepare keyword list + threshold
        keywords = cfg.get("sensitive_keywords", [])
        self.min_score = min_score

        # 3) initialize the engine
        self.analyzer = AnalyzerEngine()

        # 4) build Presidio Pattern objects from content‐classifier style regexes
        kw_patterns = []
        for kw in keywords:
            esc = re.escape(kw)
            regex = rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])"
            kw_patterns.append(
                Pattern(name=kw, regex=regex, score=self.min_score)
            )

        # 5) register the PatternRecognizer
        if kw_patterns:
            self.analyzer.registry.add_recognizer(
                PatternRecognizer(
                    supported_entity="KEYWORDS_SENSITIVE",
                    supported_language="en",
                    patterns=kw_patterns,
                )
            )
        
        # 5b) add currency recognizer
        currency_patterns = [
            Pattern(name="USD", regex=r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?", score=self.min_score),
            Pattern(name="EUR", regex=r"€\s?\d+(?:,\d{3})*(?:\.\d{2})?", score=self.min_score),
            Pattern(name="GBP", regex=r"£\s?\d+(?:,\d{3})*(?:\.\d{2})?", score=self.min_score),
            Pattern(name="JPY", regex=r"¥\s?\d+(?:,\d{3})*(?:\.\d{2})?", score=self.min_score),
        ]
        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="CURRENCY",
                supported_language="en",
                patterns=currency_patterns,
            )
        )

        # 5c) add password recognizer
        password_pattern = Pattern(
            name="PASSWORD",
            regex=r"(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}",
            score=self.min_score
        )
        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="PASSWORD",
                supported_language="en",
                patterns=[password_pattern],
            )
        )

        # 5d) add disease synonym recognizer using WordNet

        class DiseaseSynonymRecognizer(PatternRecognizer):
            def __init__(self, min_score=0.2):
                # Get synonyms for "disease" from WordNet
                disease_synonyms = set()
                for syn in wordnet.synsets("disease"):
                    for lemma in syn.lemma_names():
                        disease_synonyms.add(lemma.replace("_", " ").lower())
                patterns = [
                    Pattern(
                        name=syn,
                        regex=rf"(?<![A-Za-z0-9]){re.escape(syn)}(?![A-Za-z0-9])",
                        score=min_score
                    )
                    for syn in disease_synonyms
                ]
                super().__init__(
                    supported_entity="DISEASE_SYNONYM",
                    supported_language="en",
                    patterns=patterns
                )

        self.analyzer.registry.add_recognizer(
            DiseaseSynonymRecognizer(min_score=self.min_score)
        )

        # 6) register the lemma/synonym-based keyword recognizer too
        self.analyzer.registry.add_recognizer(
            PrivacyKeywordRecognizer(
                keywords=keywords,
                supported_language="en",
            )
        )


    def classify(self, filepath: str) -> str:
        
        # extension check
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.sensitive_exts:
            return "SENSITIVE"

        # extract
        text = ExtractTextFromFiles.extract_text(filepath)

        # analyze both pattern + keyword recognizers
        results = self.analyzer.analyze(text=text, language="en", allow_list= ["emails", "email", "Finish"])

        # threshold decision
       
        for r in results:
            if r.entity_type != "DATE_TIME" \
               and r.entity_type != "LOCATION" \
               and r.score >= self.min_score:
                return "SENSITIVE"
        return "INSENSITIVE"

    def returnAnalyzerResults(self, filepath: str):
        text = ExtractTextFromFiles.extract_text(filepath)
        return self.analyzer.analyze(text=text, language="en")

    def returnAllRecognizers(self):
        return self.analyzer.registry.get_recognizers(
            language="en", all_fields=True
        )