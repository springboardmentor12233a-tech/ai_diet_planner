from ocr.ocr_engine import extract_text_from_image, extract_text_from_pdf
from utils.text_cleaner import clean_text
from nlp.advice_extractor import extract_advice_lines
from nlp.intent_mapper import map_text_to_intents
from generator.diet_plan_generator import generate_diet_plan

def manual_input():
    print("Enter doctor's advice (type END to finish):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def main():
    print("Choose input type:")
    print("1. Image")
    print("2. PDF")
    print("3. Manual Entry")

    choice = input("Enter choice: ").strip()

    raw_text = ""

    if choice == "1":
        path = input("Enter image path: ")
        raw_text = extract_text_from_image(path)

    elif choice == "2":
        path = input("Enter PDF path: ")
        raw_text = extract_text_from_pdf(path)

    elif choice == "3":
        raw_text = manual_input()

    else:
        print("Invalid choice")
        return


    cleaned = clean_text(raw_text)
    print("\n===== RAW OCR TEXT =====\n")
    print(raw_text)
    advice_lines = extract_advice_lines(cleaned)
    intents = map_text_to_intents(cleaned)
    diet_plan = generate_diet_plan(intents)

    print("\n===== DIET PLAN =====\n")
    for section, items in diet_plan.items():
        print(section + ":")
        if items:
            for i in items:
                print("-", i)
        else:
            print("- No specific items")
        print()

if __name__ == "__main__":
    main()
