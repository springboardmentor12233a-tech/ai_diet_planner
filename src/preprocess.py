import re

def preprocess_text(text):
    print("\n--- RAW OCR TEXT ---")
    print(text)

    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9./\s()-]', ' ', text)

    print("\n--- PREPROCESSED TEXT ---")
    print(text)

    return text


def extract_parameters(text):
    patterns = {
        "Hemoglobin": r'hemoglobin\s*[:\-]?\s*(\d+\.?\d*)\s*(g/dl)?',
        "Total WBC Count": r'total wbc count\s*[:\-]?\s*(\d+\.?\d*)\s*(/cumm)?',
        "Platelet Count": r'platelet count\s*[:\-]?\s*(\d+\.?\d*)\s*(lakhs/cmm)?',
        "AST (SGOT)": r'(ast|sgot)\s*[:\-]?\s*(\d+\.?\d*)',
        "ALT (SGPT)": r'(alt|sgpt)\s*[:\-]?\s*(\d+\.?\d*)',
        "Glucose": r'glucose\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?',
        "LDL": r'ldl\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl)?'
    }

    records = []

    print("\n--- PARAMETER EXTRACTION ---")

    for test_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1)
            unit = match.group(2) if match.group(2) else ""

            print(f"[FOUND] {test_name}")
            print(f"        Value: {value}")
            print(f"        Unit : {unit}")

            records.append({
                "Test Name": test_name,
                "Observed Value": value,
                "Unit": unit
            })
        else:
            print(f"[NOT FOUND] {test_name}")

    return records
