# Location: services/classification_service.py
from Services.ModelClassifier import ModelClassifier
from Services.PresidioClassifier import PresidioClassifier
class ClassificationService:
    def __init__(self, classifier=None):
        self.classifier = classifier or PresidioClassifier()

    def classify(self, file_path: str) -> str:
        return self.classifier.classify(file_path)
