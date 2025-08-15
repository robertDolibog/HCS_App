import os
from PyPDF2 import PdfReader
import docx


class ExtractTextFromFiles:

    def extract_text(filepath: str) -> str:
            ext = os.path.splitext(filepath)[1].lower()
            try:
                if ext == ".txt":
                    with open(filepath, encoding="utf-8", errors="ignore") as f:
                        return f.read()

                elif ext == ".pdf":
                    reader = PdfReader(filepath)
                    return " ".join(page.extract_text() or "" for page in reader.pages)

                elif ext == ".docx":
                    doc = docx.Document(filepath)
                    return " ".join(p.text for p in doc.paragraphs)

            except Exception:
                return ""
            return ""