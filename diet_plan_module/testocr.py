from ocr.ocr_engine import extract_text_from_image

image_path = r"E:\InfosysSpringboard-Project\Datasets\iron_disease.jpg"

text = extract_text_from_image(image_path)

print("\n===== OCR OUTPUT =====\n")
print(text)
