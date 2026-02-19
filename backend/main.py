import easyocr

print("Loading EasyOCR Model...")

reader = easyocr.Reader(
    ['en'],
    gpu=False   
)

print("EasyOCR Loaded Successfully")
