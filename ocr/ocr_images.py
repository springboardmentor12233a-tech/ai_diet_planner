from pathlib import Path
from PIL import Image
import pytesseract as tess


base_dir = Path(__file__).resolve().parents[1] # Get the base directory two levels up
image_dir = base_dir / "datasets" / "images" # Directory containing images

for img_path in image_dir.iterdir():
    if img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        img = Image.open(img_path)
        
        
        text = tess.image_to_string(img)

        print(f"\n--- {img_path.name} ---")
        print(text)

