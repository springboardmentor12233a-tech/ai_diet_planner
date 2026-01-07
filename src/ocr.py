import easyocr
import cv2

image_path = "E:\InfosysSpringboard-Project\Datasets\medical_reports_images\AHD-0425-PA-0007719_E-REPORTS_250427_2032@E.pdf_page_7.png"

reader = easyocr.Reader(['en'], gpu=False)

results = reader.readtext(image_path)

img = cv2.imread(image_path)
cv2.imshow("Uploaded Medical Report", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("\nExtracted Text:\n")

total_confidence = 0

for bbox, text, confidence in results:
    print(f"{text} (Confidence: {confidence:.2f})")
    total_confidence += confidence

if len(results) > 0:
    avg_confidence = total_confidence / len(results)
    print("\nAverage OCR Confidence:", round(avg_confidence, 2))
else:
    print("No text detected.")
