# m3_text_analyzer.py
# This file understands prescription text

def analyze_prescription(text):
    text = text.lower()

    result = {
        "limit": [],
        "increase": []
    }

    if "sugar" in text:
        result["limit"].append("sugar")

    if "fried" in text or "oily" in text:
        result["limit"].append("fried foods")

    if "salt" in text:
        result["limit"].append("salt")

    if "vegetable" in text or "fiber" in text:
        result["increase"].append("vegetables and fiber")

    return result