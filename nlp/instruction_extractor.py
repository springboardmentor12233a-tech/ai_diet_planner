import pytesseract
from PIL import Image
from pdf2image import convert_from_path

ADVICE_KEYWORDS = [
    "advise", "advised", "avoid", "reduce",
    "increase", "take", "follow", "recommended",
    "diet", "exercise", "restrict"
]

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

def extract_doctor_advice(text):
    advice_lines = []
    lines = text.split("\n")

    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ADVICE_KEYWORDS):
            advice_lines.append(line.strip())

    return advice_lines


# -------- INPUT --------
file_path = input("Enter prescription file path (PDF/Image): ").strip().strip('"')


# -------- OCR --------
if file_path.lower().endswith(".pdf"):
    full_text = extract_text_from_pdf(file_path)
elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
    full_text = extract_text_from_image(file_path)
else:
    print("Unsupported file format")
    exit()

# -------- FILTER DOCTOR ADVICE --------
doctor_advice = extract_doctor_advice(full_text)

# -------- OUTPUT --------
print("\n===== DOCTOR ADVICE EXTRACTED =====\n")

if doctor_advice:
    for line in doctor_advice:
        print("-", line)
else:
    print("No doctor advice detected.")