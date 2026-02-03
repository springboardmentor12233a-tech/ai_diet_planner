from prescription_parser import extract_diet_instructions
from diet_generator import generate_diet_plan

if __name__ == "__main__":
    prescription = "Patient should avoid sugar and oily food. Add green vegetables and protein."

    rules = extract_diet_instructions(prescription)
    plan = generate_diet_plan(rules)

    print("Diet Plan:")
    for item in plan:
        print("-", item)
