# AI/ML-Based Personalized Diet Plan Generator from Medical Reports

## Milestone 1: Data Collection and Preprocessing (Week 1–2)

### Milestone Objective
The objective of Milestone 1 is to collect medical report data from multiple sources and preprocess it into structured formats. This step prepares both numerical lab values and unstructured medical text for further ML and NLP-based health analysis.

### Datasets Used

#### 1. Structured CSV Dataset
- **Dataset Name:** Pima Indians Diabetes Database  
- **Source:** Kaggle  
- **Link:** https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database  
- **Description:** Contains medical attributes such as glucose level, blood pressure, BMI, insulin, and diabetes outcome.

#### 2. Image Dataset (Scanned Reports)
- **Dataset Name:** Medical Report Image Dataset  
- **Source:** Kaggle  
- **Link:** https://www.kaggle.com/datasets/dikshaasinghhh/bajaj  
- **Description:** Contains scanned medical reports used for OCR-based text extraction.


### Tools & Technologies Used
- Python  
- Pandas, NumPy  
- EasyOCR (for scanned report text extraction)  
- Google Colab (for OCR implementation and experimentation)


### Work Done in Milestone 1
- Collected structured medical data in CSV format and unstructured scanned medical reports  
- Loaded and explored the CSV dataset to understand numerical health parameters  
- Implemented OCR using EasyOCR to extract text from scanned medical report images  
- Identified important medical parameters such as glucose, cholesterol, protein, and pH from extracted text  
- Converted extracted information into structured key–value format suitable for ML processing  


### Outcome
At the end of Milestone 1, medical data from CSV files and scanned images was successfully extracted and converted into structured formats. This milestone establishes the foundation for ML-based health condition analysis and NLP-driven interpretation in future milestones.




