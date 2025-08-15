from abc import ABC, abstractmethod

class ClassifierInterface(ABC):
    @abstractmethod
    def classify(self, file_path: str) -> str:
        """Return sensitivity label: sensitive, insensitive"""
        pass