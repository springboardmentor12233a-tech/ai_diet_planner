import pandas as pd
import os

from .preprocess import preprocess_text, extract_parameters
from .easyocr_extractor import extract_text_from_image
from .model import train_logistic_regression
from .model import train_svm_model



def run_ocr_extraction():
    print("\n--- OCR EXTRACTION STARTED ---")

    image_path = (
        r"C:\Users\parth\Documents\virtual intern\lbmaske"
        r"\BLR-0425-PA-0039192_05c45741fa5d4b5180df06f200423a00__2_files_merged__26-04-2025_0430-01_PM@E.pdf_page_104.png"
    )

    img_text = extract_text_from_image(image_path)

    records = extract_parameters(preprocess_text(img_text))

    df = pd.DataFrame(records)

    output_dir = r"C:\Users\parth\Documents\virtual intern\ai_diet_planner\output"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "data.csv")
    df.to_csv(output_file, index=False)

    print(f"OCR extraction completed. Tests extracted: {len(df)}")
    print(f"Saved to: {output_file}")


def run_model_training():
    print("\n--- TRAINING LOGISTIC REGRESSION MODEL ---")

    dataset_path = r"C:\Users\parth\Documents\virtual intern\diabetes.csv"

    #accuracy, report = train_logistic_regression(dataset_path)
    accuracy, report = train_svm_model(dataset_path)

    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:\n")
    print(report)


def main():
    run_ocr_extraction()
    run_model_training()


if __name__ == "__main__":
    main()
