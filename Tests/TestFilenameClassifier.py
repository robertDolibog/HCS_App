from Services.FilenameClassifier import FilenameClassifier
import os
import csv

dataset_dir = "TestData"
from Services.MetadataClassifier import MetadataClassifier
sensitive_dir = os.path.join(dataset_dir, "sensitive")
insensitive_dir = os.path.join(dataset_dir, "insensitive")

truth = {}
with open(os.path.join(dataset_dir, "ground_truth.csv"), newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        truth[row["filename"]] = row["sensitivity"]


# === Initialize classifiers ===
FilenameClassifier = FilenameClassifier()


correct = 0
total = 0
# Simulate processing files in the sensitive and insensitive directories
for folder in [sensitive_dir, insensitive_dir]:
    for i in range(5):
        # Simulate processing files
        print(f"Processing {folder}, file {i}")
        # Simulate classification
        for filename in os.listdir(folder):
            full_path = os.path.join(folder, filename)
            if not os.path.isfile(full_path):
                continue
            prediction = FilenameClassifier.classify(full_path)
            print (f"Predicted: {prediction} for {filename}")
            actual = truth.get(filename)
            if actual is None:
                continue
            if prediction == actual:
                correct += 1
            total += 1
accuracy = (correct / total * 100) if total > 0 else 0.0
print(f"FilenameClassifier: {correct}/{total} correct ({accuracy:.2f}%)")