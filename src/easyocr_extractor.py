import easyocr
import cv2

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    result = reader.readtext(image, detail=0)
    return " ".join(result)
