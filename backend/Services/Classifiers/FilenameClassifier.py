import os
import json
import re
from .ClassifierInterface import ClassifierInterface

class FilenameClassifier(ClassifierInterface):
    def __init__(self,
                 config_path=os.path.join(os.path.dirname(__file__), "sensitivity_keywords.json")):
        # Load JSON config
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        # Normalize extensions to lowercase and ensure they start with a dot
        self.sensitive_exts = {
            ext.lower() if ext.startswith('.') else f".{ext.lower()}"
            for ext in self.config.get("sensitive_extensions", [])
        }

        # Build a single list of compiled regexes:
        #  wrap each keyword in \b…\b so "SSN" doesn't match "passportssn"

        patterns = []

        for kw in self.config.get("sensitive_keywords", []):
            # escape the keyword then add word‐boundary anchors
            kw_esc = re.escape(kw)
            patterns.append(rf"(?<![A-Za-z0-9]){kw_esc}(?![A-Za-z0-9])")

        

        # Compile all patterns case‐insensitively
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    def classify(self, file_path: str) -> str:
        name = os.path.basename(file_path)
        ext = os.path.splitext(name)[1].lower()

        # 1. Extension‐based rule
        if ext in self.sensitive_exts:
            return "SENSITIVE"

        # 2. Regex‐based rules (covers both keywords and custom patterns)
        for regex in self.patterns:
            if regex.search(name):
                return "SENSITIVE"

        # 3. Default
        return "INSENSITIVE"
