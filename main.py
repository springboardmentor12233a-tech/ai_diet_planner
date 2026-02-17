from input_handlers.image_reader import read_image
from input_handlers.pdf_reader import read_pdf
from input_handlers.text_reader import read_text

from parsers.text_cleaner import clean_text
from parsers.prescription_parser import parse_prescription

from diet_engine.meal_selector import load_dataset, recommend_meals

# ===== SELECT INPUT TYPE =====
INPUT_TYPE = "image"   # image | pdf | text

if INPUT_TYPE == "image":
    raw_text = read_image("C:/Users/toshu/Downloads/iron_disease.jpg")

elif INPUT_TYPE == "pdf":
    raw_text = read_pdf("sample_report.pdf")

else:
    raw_text = read_text("""
    Tab Livogen 1-0-1 after food for 10 days
    Avoid tea and coffee
    Iron deficiency anemia
    """)

# ===== PROCESS =====
cleaned_text = clean_text(raw_text)
parsed_data = parse_prescription(cleaned_text)

print("\n--- PARSED PRESCRIPTION ---")
print(parsed_data)

# ===== DIET RECOMMENDATION =====
df = load_dataset("E:/InfosysSpringboard-Project/Datasets/nutrition.xlsx")
meals = recommend_meals(df, parsed_data["conditions"])
print("\n--- RECOMMENDED MEALS ---")
print(meals[["meal_name", "calories", "protein_g"]])

print("\n⚠️ This is an AI-generated diet suggestion and not a medical prescription.")
