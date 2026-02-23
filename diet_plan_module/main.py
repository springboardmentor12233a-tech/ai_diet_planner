# from ocr.ocr_engine import extract_text_from_image, extract_text_from_pdf
# from utils.text_cleaner import clean_text
# from nlp.advice_extractor import extract_advice_lines
# from nlp.intent_mapper import map_text_to_intents
# from generator.diet_plan_generator import generate_diet_plan

# def manual_input():
#     print("Enter doctor's advice (type END to finish):")
#     lines = []
#     while True:
#         line = input()
#         if line.strip().upper() == "END":
#             break
#         lines.append(line)
#     return "\n".join(lines)

# def main():
#     print("Choose input type:")
#     print("1. Image")
#     print("2. PDF")
#     print("3. Manual Entry")

#     choice = input("Enter choice: ").strip()

#     raw_text = ""

#     if choice == "1":
#         path = input("Enter image path: ")
#         raw_text = extract_text_from_image(path)

#     elif choice == "2":
#         path = input("Enter PDF path: ")
#         raw_text = extract_text_from_pdf(path)

#     elif choice == "3":
#         raw_text = manual_input()

#     else:
#         print("Invalid choice")
#         return


#     cleaned = clean_text(raw_text)
#     print("\n===== RAW OCR TEXT =====\n")
#     print(raw_text)
#     advice_lines = extract_advice_lines(cleaned)
#     intents = map_text_to_intents(cleaned)
#     diet_plan = generate_diet_plan(intents)

#     print("\n===== DIET PLAN =====\n")
#     for section, items in diet_plan.items():
#         print(section + ":")
#         if items:
#             for i in items:
#                 print("-", i)
#         else:
#             print("- No specific items")
#         print()

# if __name__ == "__main__":
#     main()


# import sys
# import os
# import random

# # Ensure project root is in path (for src imports)
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if PROJECT_ROOT not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT)

# from ocr.ocr_engine import extract_text_from_image, extract_text_from_pdf
# from utils.text_cleaner import clean_text
# # from nlp.advice_extractor import extract_advice_lines
# # from nlp.intent_mapper import map_text_to_intents
# # from generator.diet_plan_generator import generate_diet_plan
# # from integration.condition_aggregator import aggregate_conditions

# # ML integration
# try:
#     from src.inference.analyze_patient import get_patient_input, predict_diabetes
#     ML_AVAILABLE = True
# except ImportError:
#     ML_AVAILABLE = False


# # ----------------------------
# # Manual Input
# # ----------------------------
# def manual_input():
#     print("Enter doctor's advice (type END to finish):")
#     lines = []
#     while True:
#         line = input()
#         if line.strip().upper() == "END":
#             break
#         lines.append(line)
#     return "\n".join(lines)


# # ----------------------------
# # Structured Plan Printer
# # ----------------------------
# def print_diet_plan(diet_plan):
#     print("\n===== DIET PLAN =====\n")
#     for section, items in diet_plan.items():
#         print(section + ":")
#         if items:
#             for i in items:
#                 print("-", i)
#         else:
#             print("- No specific items")
#         print()


# # ----------------------------
# # Expand 1-Day Plan to 7 Days
# # ----------------------------
# def expand_to_week(one_day_text):
#     lines = one_day_text.split("\n")
#     base = {}

#     for line in lines:
#         if ":" in line:
#             key, value = line.split(":", 1)
#             base[key.strip()] = value.strip()

#     weekly = ""

#     for i in range(1, 8):
#         weekly += f"\nDay {i}:\n"

#         for section in ["Breakfast", "Lunch", "Snack", "Dinner"]:
#             items = base.get(section, "")
#             item_list = [x.strip() for x in items.split(",") if x.strip()]
#             random.shuffle(item_list)
#             weekly += f"{section}: {', '.join(item_list)}\n"

#         weekly += f"Avoid: {base.get('Avoid', '')}\n"
#         weekly += f"Notes: {base.get('Notes', '')}\n"

#     return weekly


# # ----------------------------
# # Main
# # ----------------------------
# def main():
#     print("Choose input type:")
#     print("1. Image")
#     print("2. PDF")
#     print("3. Manual Entry")

#     choice = input("Enter choice: ").strip()
#     raw_text = ""

#     if choice == "1":
#         path = input("Enter image path: ")
#         raw_text = extract_text_from_image(path)

#     elif choice == "2":
#         path = input("Enter PDF path: ")
#         raw_text = extract_text_from_pdf(path)

#     elif choice == "3":
#         raw_text = manual_input()

#     else:
#         print("Invalid choice")
#         return

#     cleaned = clean_text(raw_text)

#     print("\n===== RAW OCR TEXT =====\n")
#     print(raw_text)

#     # advice_lines = extract_advice_lines(cleaned)
#     # intents = map_text_to_intents(cleaned)

#     # ----------------------------
#     # ML DIABETES INTEGRATION
#     # ----------------------------
#     # ml_result = None

#     # if ML_AVAILABLE:
#     #     use_ml = input("\nDo you want to enter health metrics for diabetes prediction? (y/n): ").lower()
#     #     if use_ml == "y":
#     #         patient = get_patient_input()
#     #         ml_result = predict_diabetes(patient)

#     #         print("\n===== DIABETES PREDICTION =====")
#     #         print("Diabetic:", ml_result["is_diabetic"])
#     #         print("Risk Probability:", round(ml_result["risk_probability"], 2))

#     # # Combine NLP + ML conditions
#     # final_conditions = aggregate_conditions(intents, ml_result)

#     # # Generate structured diet
#     # diet_plan = generate_diet_plan(final_conditions)

# # ----------------------------
# # SIMPLE LLM GENERATION
# # ----------------------------

#     use_ai = input("\nGenerate AI diet plan using LLM? (y/n): ").lower()

#     if use_ai == "y":

#         duration_choice = input("Choose duration (1 / 3 / 5 / 7 days): ").strip()

#         if duration_choice not in ["1", "3", "5", "7"]:
#             print("Invalid choice. Defaulting to 1 day.")
#             duration_choice = "1"

#         try:
#             from ai_refiner.simple_llm_generator import generate_diet_plan_from_note

#             print("\nGenerating AI diet plan... Please wait (10-20 seconds)...\n")

#             refined_output = generate_diet_plan_from_note(raw_text, duration_choice)

#             print("\n===== AI GENERATED DIET PLAN =====\n")
#             print(refined_output)

#         except Exception as e:
#             print("AI generation failed:", str(e))

#     else:
#         print_diet_plan(diet_plan)



# if __name__ == "__main__":
#     main()



import sys
import os

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ocr.ocr_engine import extract_text_from_image, extract_text_from_pdf
from utils.text_cleaner import clean_text


# ----------------------------
# Manual Input
# ----------------------------
def manual_input():
    print("Enter doctor's advice or medical report (type END to finish):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


# ----------------------------
# Main
# ----------------------------
def main():

    print("Choose input type:")
    print("1. Image")
    print("2. PDF")
    print("3. Manual Entry")

    choice = input("Enter choice: ").strip()
    raw_text = ""

    # ----------------------------
    # Input Handling
    # ----------------------------
    if choice == "1":
        path = input("Enter image path: ").strip()
        raw_text = extract_text_from_image(path)

    elif choice == "2":
        path = input("Enter PDF path: ").strip()
        raw_text = extract_text_from_pdf(path)

    elif choice == "3":
        raw_text = manual_input()

    else:
        print("Invalid choice.")
        return

    if not raw_text.strip():
        print("No text extracted.")
        return

    cleaned = clean_text(raw_text)

    print("\n===== EXTRACTED TEXT =====\n")
    print(cleaned)

    # ----------------------------
    # LLM Generation
    # ----------------------------
    use_ai = input("\nGenerate AI diet plan using LLM? (y/n): ").lower()

    if use_ai != "y":
        print("AI generation cancelled.")
        return

    duration_choice = input("Choose duration (1 / 3 / 5 / 7 days): ").strip()

    if duration_choice not in ["1", "3", "5", "7"]:
        print("Invalid choice. Defaulting to 7 days.")
        duration_choice = "7"

    try:
        from ai_refiner.simple_llm_generator import generate_diet_plan_from_note

        print("\nGenerating AI diet plan... Please wait...\n")

        diet_output = generate_diet_plan_from_note(cleaned, duration_choice)

        print("\n===== AI GENERATED DIET PLAN =====\n")
        print(diet_output)

    except Exception as e:
        print("AI generation failed:", str(e))


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    main()
