from presidio_analyzer import RecognizerResult, AnalysisExplanation
from presidio_analyzer.entity_recognizer import EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import List, Optional
from nltk.corpus import wordnet

class PrivacyKeywordRecognizer(EntityRecognizer):
    def __init__(self,
        keywords: List[str],
        supported_language: str = "en",
        name: Optional[str] = "PrivacyKeywordRecognizer",
        version: str = "1.0.0",
    ):
        super().__init__(
            supported_entities=["KEYWORDS_SENSITIVE"],
            supported_language=supported_language,
            name=name,
            version=version,
        )
        self.keywords = {w.lower() for w in keywords}
        self.exact_score = 0.9
        self.synonym_score = 0.6

    def load(self):
        pass  # nothing to preload

    def build_explanation(self, score: float, detail: str) -> AnalysisExplanation:
        return AnalysisExplanation(
            recognizer=self.name,
            original_score=score,
            textual_explanation=detail,
        )

    def analyze(self,
        text: str,
        entities: List[str],
        nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        

        results = []
        tokens = nlp_artifacts.tokens
        lemmas = [l.lower() for l in nlp_artifacts.lemmas]

        for i, lemma in enumerate(lemmas):
            token = tokens[i]
            if lemma in self.keywords:
                score = self.exact_score
                reason = f"Exact keyword match for '{token.text}'"

            else:
                continue
            """    excluded as per processing time limitations.
            else:
                # 2) Synonym checks: collect all synonyms for debug
                syns = []
                for synset in wordnet.synsets(lemma):
                    for l in synset.lemmas():
                        syns.append(l.name().lower().replace("_", " "))
                syns = sorted(set(syns))
                #print(f"Checking synonyms for '{lemma}': {syns}")

                # find which synonyms match keywords
                matched = [s for s in syns if s in self.keywords]
                if matched:
                    score = self.synonym_score
                    reason = (
                        f"WordNet synonym match for '{token.text}', matched {matched}"
                    )
                else:
                    continue
            """

            explanation = self.build_explanation(score, reason)
            results.append(
                RecognizerResult(
                    entity_type="KEYWORDS_SENSITIVE",
                    start=token.idx,
                    end=token.idx + len(token.text),
                    score=score,
                    analysis_explanation=explanation,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id
                    },
                )
            )

        return results