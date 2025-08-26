from Services.Classifiers.ModelClassifier import ModelClassifier
from Services.Classifiers.PresidioClassifier import PresidioClassifier
from Services.Classifiers.MixedClassifier import MixedClassifier
class ClassificationService:
    def __init__(self, classifier=None):
        self.classifier = classifier or MixedClassifier()

    def classify(self, file_path: str) -> str:
        return self.classifier.classify(file_path)
