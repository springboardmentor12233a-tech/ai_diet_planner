# -*- coding: utf-8 -*-
"""
Milestone3.py
Converted from Colab notebook to VS Code runnable script
"""

import os
import re
import cv2
import torch
import pytesseract
import pandas as pd
import numpy as np
import nltk
from transformers import BertTokenizer, BertModel
from sklearn.model_selection import train_test_split

# Download stopwords if not already present
nltk.download('stopwords')
from nltk.corpus import stopwords

# -----------------------------
# Sample Data
# -----------------------------
data = {
    "doctor_note": [
        "Avoid oily food and reduce sugar intake",
        "Include more green vegetables and fruits",
        "Limit salt consumption",
        "Drink plenty of water",
        "Avoid junk food and sugary drinks",
        "Eat more protein-rich foods like beans and lentils",
        "Limit red meat consumption",
        "Include whole grains in your diet",
        "Avoid excessive caffeine",
        "Practice portion control during meals"
    ],
    "diet_rule": [
        "avoid_oily_food, limit_sugar",
        "include_vegetables, include_fruits",
        "limit_salt",
        "increase_water",
        "avoid_junk_food, avoid_sugary_drinks",
        "include_protein_foods",
        "limit_red_meat",
        "include_whole_grains",
        "limit_caffeine",
        "practice_portion_control"
    ]
}


df = pd.DataFrame(data)

# -----------------------------
# Text Cleaning
# -----------------------------
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

df["clean_text"] = df["doctor_note"].apply(clean_text)

# -----------------------------
# Train-Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    df["clean_text"],
    df["diet_rule"],
    test_size=0.2,
    random_state=42
)

# -----------------------------
# BERT Embeddings
# -----------------------------
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

X_train_embed = np.array([get_bert_embedding(text) for text in X_train])
X_test_embed = np.array([get_bert_embedding(text) for text in X_test])

# -----------------------------
# Rule Mapping
# -----------------------------
def map_to_diet_rule(text):
    rules = []
    if "avoid" in text and "oil" in text:
        rules.append("avoid_oily_food")
    if "sugar" in text:
        rules.append("limit_sugar")
    if "vegetable" in text:
        rules.append("include_vegetables")
    if "fruit" in text:
        rules.append("include_fruits")
    if "salt" in text:
        rules.append("limit_salt")
    if "water" in text:
        rules.append("increase_water")
    if "junk" in text:
        rules.append("avoid_junk_food")
    return ",".join(rules)

predicted_rules = X_test.apply(map_to_diet_rule)

# -----------------------------
# Accuracy Calculation
# -----------------------------
def calculate_accuracy(true, predicted):
    correct = 0
    for t, p in zip(true, predicted):
        t_set = set(t.split(","))
        p_set = set(p.split(","))
        if len(t_set & p_set) > 0:  # at least one rule matches
            correct += 1
    return correct / len(true)

def rule_conversion_accuracy(true, predicted):
    total = 0
    matched = 0
    for t, p in zip(true, predicted):
        t_rules = t.split(",")
        p_rules = p.split(",")
        total += len(t_rules)
        matched += len(set(t_rules) & set(p_rules))
    return matched / total

# -----------------------------
# OCR + Diet Rule Extraction
# -----------------------------
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return pytesseract.image_to_string(gray)

def map_to_diet_rules(text):
    rules = []
    if "avoid" in text and "oil" in text:
        rules.append("Avoid oily food")
    if "sugar" in text:
        rules.append("Limit sugar intake")
    if "salt" in text:
        rules.append("Limit salt intake")
    if "fruit" in text:
        rules.append("Include fruits")
    if "vegetable" in text:
        rules.append("Include vegetables")
    if "water" in text:
        rules.append("Drink more water")
    if "junk" in text:
        rules.append("Avoid junk food")
    return rules

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    # Accuracy results
    acc1 = calculate_accuracy(y_test.values, predicted_rules.values)
    acc2 = rule_conversion_accuracy(y_test.values, predicted_rules.values)
    print("Accuracy:", acc1 * 100)
    print("Rule Conversion Accuracy:", acc2 * 100)

    # -----------------------------
    # User Input Option
    # -----------------------------
    user_input = input("\nEnter doctor note text (or press Enter to skip): ").strip()
    if user_input:
        cleaned_text = clean_text(user_input)
        diet_rules = map_to_diet_rules(cleaned_text)
        print("\n✅ Actionable Diet Guidelines (from text input):\n")
        for rule in diet_rules:
            print("-", rule)
    else:
        # OCR Example (replace with your image path)
        image_path = "doctor_note_sample.png"  # <-- put your image file here
        if os.path.exists(image_path):
            extracted_text = extract_text_from_image(image_path)
            cleaned_text = clean_text(extracted_text)
            diet_rules = map_to_diet_rules(cleaned_text)
            print("\n✅ Actionable Diet Guidelines (from OCR):\n")
            for rule in diet_rules:
                print("-", rule)
        else:
            print("\nNo image found for OCR. Place an image as 'doctor_note_sample.png'.")
