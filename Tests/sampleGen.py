# generate_full_dataset.py
# Scientifically structured generator for synthetic sensitivity dataset
# 150 files: 50 SENSITIVE + 50 INSENSITIVE in .txt, .pdf, .docx formats
# Filenames now all sound generic to avoid name‐based leakage

import os
import random
import csv
from fpdf import FPDF
from docx import Document

random.seed(42)  # For reproducibility

# === Setup directories ===
base_dir = "TestData"
sensitive_dir = os.path.join(base_dir, "sensitive")
insensitive_dir = os.path.join(base_dir, "insensitive")
os.makedirs(sensitive_dir, exist_ok=True)
os.makedirs(insensitive_dir, exist_ok=True)

# === Content templates ===
sensitive_templates = [
    "Employee Name: {name}\nIBAN: {iban}\nMonthly Salary: ${amount}",
    "Passport Number: {passport}\nFull Name: {name}\nNationality: {country}",
    "Login Credentials\nUsername: {username}\nPassword: {password}",
    "Insurance Policy\nName: {name}\nPolicy No: {policy}\nCoverage: Full",
    "Medical Report\nPatient: {name}\nDiagnosis: {diagnosis}\nTreatment: {treatment}"
]

insensitive_templates = [
    "Weekly Grocery List\n- {item1}\n- {item2}\n- {item3}",
    "Travel Itinerary\nDestination: {city}\nDuration: {days} days\nNotes: {notes}",
    "Recipe: {dish}\nIngredients: {ingredients}\nSteps: {steps}",
    "Book Summary\nTitle: {title}\nTheme: {theme}\nNotes: {summary}",
    "Workout Plan\nDay 1: {exercise1}\nDay 2: {exercise2}\nDay 3: {exercise3}"
]

# === Filename tokens (shared pool) ===
GENERIC_TOKENS = [
    "report", "plan", "overview", "notes", "summary",
    "meeting", "presentation", "draft", "agenda", "document"
]

# === Ground truth collector ===
csv_rows = []

# === Content generators ===
def generate_sensitive_content():
    return random.choice(sensitive_templates).format(
        name=random.choice(["John Doe", "Alice Müller", "Omar Youssef", "Marie Curie"]),
        iban=f"DE{random.randint(10_000_000_000, 99_999_999_999)}",
        amount=random.choice(["2800", "4200", "5600"]),
        passport=f"X{random.randint(1000000, 9999999)}",
        country=random.choice(["Germany", "France", "USA", "Japan"]),
        username=random.choice(["jdoe", "alice.m", "user2023"]),
        password=random.choice(["pass123", "secure@2023", "hunter2"]),
        policy=f"POL{random.randint(10000,99999)}",
        diagnosis=random.choice(["Diabetes", "Hypertension", "Asthma"]),
        treatment=random.choice(["Medication", "Diet", "Therapy"])
    )

def generate_insensitive_content():
    return random.choice(insensitive_templates).format(
        item1="Milk", item2="Eggs", item3="Bread",
        city=random.choice(["Rome", "Oslo", "Paris"]),
        days=random.randint(3,14),
        notes=random.choice(["Check museum hours", "Book hotel early"]),
        dish=random.choice(["Pasta Carbonara", "Chili Stew"]),
        ingredients=", ".join(random.sample(["Tomato", "Beef", "Garlic", "Onion", "Carrot"], 3)),
        steps="Mix all ingredients and simmer.",
        title=random.choice(["The Alchemist", "1984"]),
        theme=random.choice(["Freedom vs Control", "Personal Legend"]),
        summary=random.choice(["Strong symbolism throughout.", "Narrative-driven."]),
        exercise1="Push-ups", exercise2="Yoga", exercise3="Running"
    )

# === Writers ===
def create_txt(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_pdf(path, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line, ln=1)
    pdf.output(path)

def create_docx(path, content):
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(path)

# === Filename generator ===
def get_filename(i):
    token = random.choice(GENERIC_TOKENS)
    return f"{token}_{i}"

# === File generator ===
def generate_files(label, directory, content_fn):
    for i in range(1, 51):
        base = get_filename(i)
        content = content_fn()
        for ext, writer in [("txt", create_txt), ("pdf", create_pdf), ("docx", create_docx)]:
            filename = f"{base}.{ext}"
            writer(os.path.join(directory, filename), content)
            csv_rows.append([filename, label.upper(), ext])

# === Run generation ===
generate_files("SENSITIVE", sensitive_dir, generate_sensitive_content)
generate_files("INSENSITIVE", insensitive_dir, generate_insensitive_content)

# === Write ground truth ===
with open(os.path.join(base_dir, "ground_truth.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "sensitivity", "format"])
    writer.writerows(csv_rows)

print("✅ Dataset generated: 100 files with realistic generic names (+ ground_truth.csv)")
