from presidio_analyzer import AnalyzerEngine

from presidio_analyzer.nlp_engine import NlpEngineProvider

from Services.PresidioClassifier import PresidioClassifier

from Services.Helpers.ExtractTextFromFiles import ExtractTextFromFiles

from pathlib import Path

PresidioClassifier = PresidioClassifier()

AnalyzerEngine = AnalyzerEngine()


provider = NlpEngineProvider()
nlp_engine = provider.create_engine()





file_path = Path("TestData") / "sensitive" / "Document_20241128_v1_rkumar.txt"



analyserResults = PresidioClassifier.returnAnalyzerResults(file_path)


text = ExtractTextFromFiles.extract_text(file_path)
print (text)



nlp_artifacts = nlp_engine.process_text(text, "en")
print ()
print (nlp_artifacts.to_json())
print ()


# Print each sensitive match
print("===== SENSITIVE SPANS =====")
for r in analyserResults:
    span = text[r.start : r.end]
    print(f"{r.entity_type}: '{span}' (score={r.score:.2f})")






print()
print (analyserResults)
print (PresidioClassifier.classify(file_path))


