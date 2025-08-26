
import os
import re
import json

from .ClassifierInterface import ClassifierInterface
from ..Helpers.ExtractTextFromFiles import ExtractTextFromFiles

class ContentClassifier(ClassifierInterface):
    def __init__(self,
                 config_path=os.path.join(os.path.dirname(__file__), "sensitivity_keywords.json")):
        
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)

        # Normalize extensions
        self.sensitive_exts = {
            ext.lower() if ext.startswith('.') else f".{ext.lower()}"
            for ext in cfg.get("sensitive_extensions", [])
        }

        # Build boundary‑aware regex patterns for each keyword
        kw_patterns = []
        for kw in cfg.get("sensitive_keywords", []):
            esc = re.escape(kw)
            # match whole words, treating non‑alphanumerics as boundaries
            kw_patterns.append(rf"(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])")

    

    def classify(self, file_path: str) -> str:
        """
        Returns "SENSITIVE" if either:
          • the file’s extension is in sensitive_extensions, or
          • any of the sensitive_keywords matches in the content.
        Otherwise returns "INSENSITIVE".
        """
        name = os.path.basename(file_path)
        ext = os.path.splitext(name)[1].lower()

        ## 1) Extension‑based sensitivity
        if ext in self.sensitive_exts:
            return "SENSITIVE"

        # 2) Content‑based sensitivity
        text = ExtractTextFromFiles.extract_text(file_path)
        for regex in self.patterns:
            if regex.search(text):
                return "SENSITIVE"

        # 3) Default
        return "INSENSITIVE"
