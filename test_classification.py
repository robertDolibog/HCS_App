import os
import sys
import csv
import time
from collections import Counter

# Add the parent directory to the Python path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.Services.Classifiers.FilenameClassifier import FilenameClassifier
from backend.Services.Classifiers.MixedClassifier import MixedClassifier
from backend.Services.Classifiers.ContentClassifier import ContentClassifier   
from backend.Services.Classifiers.PresidioClassifier import PresidioClassifier
from backend.Services.Classifiers.ModelClassifier import ModelClassifier

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# === Configuration ===
dataset_dir = "TestData"
ground_truth_path = os.path.join(dataset_dir, "ground_truth.csv")
sensitive_dir = os.path.join(dataset_dir, "sensitive")
insensitive_dir = os.path.join(dataset_dir, "insensitive")

falseClassifications = []

# === Load ground truth ===
truth = {}
with open(ground_truth_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        truth[row["filename"]] = row["sensitivity"]

# === Initialize classifiers ===
classifiers = {
    "FilenameClassifier": FilenameClassifier(),
    "ContentClassifier": ContentClassifier(),
    "MixedClassifier": MixedClassifier(),
    "PresidioClassifier": PresidioClassifier(),
    "ModelClassifier": ModelClassifier()
}

# === Evaluation ===
def evaluate(classifier_name, classifier, labels):
    y_true = []
    y_pred = []
    correct = 0
    total = 0

    start_time = time.perf_counter()
    for folder in (sensitive_dir, insensitive_dir):
        for filename in os.listdir(folder):
            full_path = os.path.join(folder, filename)
            if not os.path.isfile(full_path):
                continue
            prediction = classifier.classify(full_path)
            actual = truth.get(filename)
            if actual is None:
                continue  # skip unknown files
            y_true.append(actual)
            y_pred.append(prediction)
            if prediction == actual:
                correct += 1
            else:
                falseClassifications.append((classifier_name, filename, prediction, actual))
            total += 1
    end_time = time.perf_counter()

    # Compute metrics
    accuracy = (correct / total * 100) if total > 0 else 0.0
    elapsed_ms = (end_time - start_time) * 1000

    # Compute confusion matrix
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[label_to_idx[t], label_to_idx[p]] += 1

    # Precision, Recall, F1 per class
    precision = []
    recall = []
    f1 = []
    for i, label in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        precision.append(prec)
        recall.append(rec)
        f1.append(f1_score)

    # Macro-averaged metrics
    macro_precision = np.mean(precision)
    macro_recall = np.mean(recall)
    macro_f1 = np.mean(f1)

    print(f"\n=== {classifier_name} ===")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Precision (per class): {dict(zip(labels, [f'{p:.2f}' for p in precision]))}")
    print(f"Recall (per class): {dict(zip(labels, [f'{r:.2f}' for r in recall]))}")
    print(f"F1 Score (per class): {dict(zip(labels, [f'{f:.2f}' for f in f1]))}")
    print(f"Macro Precision: {macro_precision:.2f}")
    print(f"Macro Recall: {macro_recall:.2f}")
    print(f"Macro F1 Score: {macro_f1:.2f}")
    print(f"Time: {elapsed_ms:.1f} ms")
    print("Confusion Matrix:")
    print("Rows: Actual, Columns: Predicted")
    print("    " + "  ".join(f"{l:>10}" for l in labels))
    for i, label in enumerate(labels):
        print(f"{label:>10} " + " ".join(f"{cm[i, j]:>10}" for j in range(len(labels))))
    return accuracy, elapsed_ms, macro_precision, macro_recall, macro_f1, cm, precision, recall, f1

# === Run evaluation ===
print(" Classifier Evaluation on Test Dataset")
# Determine all possible labels from ground truth
all_labels = sorted(set(truth.values()))

results = []
cms = {}
per_class_metrics = {}

for name, clf in classifiers.items():
    accuracy, elapsed_ms, macro_precision, macro_recall, macro_f1, cm, precision, recall, f1 = evaluate(name, clf, all_labels)
    results.append((name, accuracy, elapsed_ms, macro_precision, macro_recall, macro_f1))
    cms[name] = cm
    per_class_metrics[name] = {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

# Plot accuracy and time
names = [r[0] for r in results]
accuracies = [r[1] for r in results]
times = [r[2] for r in results]

fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel('Classifier')
ax1.set_ylabel('Accuracy (%)', color=color)
ax1.bar(names, accuracies, color=color, alpha=0.7, label='Accuracy')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 100)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Time (ms)', color=color)
ax2.plot(names, times, color=color, marker='o', label='Time')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.title('Classifier Evaluation: Accuracy and Time')
plt.show()

# Plot confusion matrices
for name in classifiers.keys():
    plt.figure(figsize=(6, 5))
    sns.heatmap(cms[name], annot=True, fmt='d', cmap='Blues',
                xticklabels=all_labels, yticklabels=all_labels)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(f'Confusion Matrix: {name}')
    plt.show()

# === Visualization of metrics for each classifier ===
metrics = ['precision', 'recall', 'f1']
for metric in metrics:
    plt.figure(figsize=(10, 6))
    for idx, label in enumerate(all_labels):
        values = [per_class_metrics[name][metric][idx] for name in names]
        plt.plot(names, values, marker='o', label=f'{label}')
    plt.ylim(0, 1)
    plt.ylabel(metric.capitalize())
    plt.xlabel('Classifier')
    plt.title(f'{metric.capitalize()} per Class for Each Classifier')
    plt.legend(title='Class')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
