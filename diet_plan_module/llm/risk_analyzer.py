import subprocess

OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "mistral"

def analyze_risk(medical_data):

    prompt = f"""
You are a clinical health assistant.

Based on this patient data:

{medical_data}

Identify possible conditions:
- Diabetes risk
- Obesity
- Hypertension
- Anemia (if possible)

Return a short list of conditions only.
"""

    result = subprocess.run(
        [OLLAMA_PATH, "run", MODEL_NAME],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return result.stdout.decode("utf-8", errors="ignore").strip()
