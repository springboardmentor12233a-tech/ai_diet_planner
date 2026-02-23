import subprocess

OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "mistral"

def generate_7_day_diet(doctor_note, medical_data, risk_summary):

    prompt = f"""
You are a certified clinical dietician.

Patient Doctor Notes:
{doctor_note}

Medical Data:
{medical_data}

Health Risk Summary:
{risk_summary}

Generate a medically appropriate 7-day diet plan.

Each day must include:
- Breakfast
- Lunch
- Snack
- Dinner
- Avoid
- Notes

Rules:
- Meals must vary across days.
- Use realistic combinations.
- Low glycemic foods if diabetes risk.
- Iron rich foods if anemia.
- Calorie deficit if overweight.
- No explanations.
- Strict structured format.

Format example:

Day 1:
Breakfast: ...
Lunch: ...
Snack: ...
Dinner: ...
Avoid: ...
Notes: ...

Continue up to Day 7.
"""

    result = subprocess.run(
        [OLLAMA_PATH, "run", MODEL_NAME],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return result.stdout.decode("utf-8", errors="ignore").strip()
