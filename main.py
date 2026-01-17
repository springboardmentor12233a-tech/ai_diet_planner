import os
import easyocr
import cv2
import ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

dataset_path = "dataset" 

print("Loading EasyOCR Model...")
reader = easyocr.Reader(['en']) # This will now download successfully
print("EasyOCR Model Loaded Successfully")

# ... (the rest of your process_manual_dataset function)


dataset_path = "dataset" 

# 2. Initialize OCR Reader
print("Loading EasyOCR Model...")
reader = easyocr.Reader(['en'])
print("EasyOCR Model Loaded Successfully")

# 3. Define valid image extensions
valid_extensions = ('.png', '.jpg', '.jpeg')

def process_manual_dataset(folder_path):
    print(f"Scanning local folder: {folder_path}")
    
    # Check if the folder actually exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' was not found in the project directory.")
        return

    count = 0
    # Walk through the local directory
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(valid_extensions):
                image_path = os.path.join(root, filename)
                
                print(f"--- Processing: {filename} ---")
                
                try:
                    # Load image
                    image = cv2.imread(image_path)
                    
                    # Extract text
                    results = reader.readtext(image)
                    
                    print("Extracted Data:")
                    for bbox, text, confidence in results:
                        if confidence > 0.5:
                            print(f"  Value: {text} (Confidence: {confidence:.2f})")
                    
                    count += 1
                    if count >= 3:
                        print("Milestone reached: 3 images processed manually.")
                        return
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    process_manual_dataset(dataset_path)