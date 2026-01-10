from csvanal import load_and_clean_csv
from ocr_utils import images_to_csv

def main():
    # Load and clean CSV
    csv_path = "data/medical_data.csv"
    df = load_and_clean_csv(csv_path)

    # Run OCR on images
    image_folder = "data/image"
    images_to_csv(image_folder, output_csv="ocr_results.csv")

if __name__ == "__main__":
    main()
