# import subprocess

# OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
# MODEL_NAME = "phi3"

# def generate_diet_plan_from_note(doctor_note: str, days: str) -> str:

#     prompt = f"""
# You are a certified clinical dietician.

# Based on the following medical report:

# {doctor_note}

# Generate a structured {days}-day diet plan.

# Each day must include:
# Breakfast
# Lunch
# Snack
# Dinner
# Avoid
# Notes

# Do not add explanations.
# Strict structured format only.

# Format:

# Day 1:
# Breakfast: ...
# Lunch: ...
# Snack: ...
# Dinner: ...
# Avoid: ...
# Notes: ...

# Continue until Day {days}.
# """

#     try:
#         result = subprocess.run(
#             [OLLAMA_PATH, "run", MODEL_NAME],
#             input=prompt.encode("utf-8"),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )

#         output = result.stdout.decode("utf-8", errors="ignore").strip()

#         if not output:
#             print("STDERR:", result.stderr.decode())
#             return "⚠ LLM returned empty response. Check if Ollama is running."

#         return output

#     except Exception as e:
#         return f"⚠ Error generating diet plan: {str(e)}"


# import subprocess

# OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
# MODEL_NAME = "phi3"

# def generate_diet_plan_from_note(doctor_note: str, days: str) -> str:

#     prompt = f"""
# You are a certified clinical dietician.

# Patient report:
# {doctor_note}

# Generate EXACTLY {days} FULL days of diet plan.

# IMPORTANT RULES:
# - You MUST write ALL days from Day 1 to Day {days}.
# - DO NOT summarize.
# - DO NOT say "Day 2-7 similar".
# - Each day must be fully written.
# - Meals must vary slightly each day.
# - Include Breakfast, Lunch, Snack, Dinner, Avoid, Notes.
# - Keep format clean and structured.
# - No explanations outside structure.

# Format:

# Day 1:
# Breakfast: ...
# Lunch: ...
# Snack: ...
# Dinner: ...
# Avoid: ...
# Notes: ...

# Continue writing Day 2, Day 3, until Day {days}.
# """

#     try:
#         result = subprocess.run(
#             [
#                 OLLAMA_PATH,
#                 "run",
#                 MODEL_NAME
#             ],
#             input=prompt.encode("utf-8"),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )

#         output = result.stdout.decode("utf-8", errors="ignore").strip()

#         if not output:
#             return "⚠ LLM returned empty response."

#         # Safety check — ensure all days exist
#         if f"Day {days}:" not in output:
#             return output + "\n\n⚠ Warning: Model did not generate all requested days."

#         return output

#     except Exception as e:
#         return f"⚠ Error generating diet plan: {str(e)}"


import subprocess

OLLAMA_PATH = r"C:\Users\toshu\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "phi3"

def generate_diet_plan(conditions, days):

    condition_text = ", ".join(conditions)

    prompt = f"""
You are a clinical dietician.

Patient conditions:
{condition_text}

Generate EXACTLY {days} days diet plan.

STRICT RULES:
- Only list food items.
- NO explanations.
- NO extra sentences.
- NO paragraphs.
- Keep each meal short (max 3-4 items).
- Different meals each day.
- Clean format only.

FORMAT:

Day 1:
Breakfast: item1, item2, item3
Lunch: item1, item2, item3
Snack: item1, item2
Dinner: item1, item2, item3
Avoid: item1, item2
Notes: short sentence only

Continue until Day {days}.
"""

    try:
        result = subprocess.run(
            [
                OLLAMA_PATH,
                "run",
                MODEL_NAME,
                "--num-predict",
                "600"   # LIMIT TOKENS → MUCH FASTER
            ],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output = result.stdout.decode("utf-8", errors="ignore").strip()

        if not output:
            return "⚠ LLM returned empty response."

        return output

    except Exception as e:
        return f"⚠ Error generating diet plan: {str(e)}"
