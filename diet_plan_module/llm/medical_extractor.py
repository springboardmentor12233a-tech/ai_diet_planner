import subprocess
import json

OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "phi3"   # or phi3

def extract_medical_data(text):

    prompt = f"""
You are a medical data extraction system.

Extract the following values from the text if available:

- Glucose
- BloodPressure
- BMI
- Age
- Insulin
- Cholesterol

Return ONLY valid JSON in this format:

{{
  "Glucose": value or null,
  "BloodPressure": value or null,
  "BMI": value or null,
  "Age": value or null,
  "Insulin": value or null,
  "Cholesterol": value or null
}}

Text:
{text}
"""

    result = subprocess.run(
        [OLLAMA_PATH, "run", MODEL_NAME],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output = result.stdout.decode("utf-8", errors="ignore")

    try:
        return json.loads(output)
    except:
        return {}
