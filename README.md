# ai_diet_planner

# Problem Statement: 
Medical reports often contain crucial numeric data (blood sugar, cholesterol, BMI) and textual notes (doctor prescriptions and comments). Patients often struggle to interpret these reports or adjust their diet accordingly. Generic diet suggestions do not account for individual medical conditions. AI-NutriCare aims to analyze patient medical reports, extract relevant information using ML and AI/NLP models, and generate a personalized diet plan that considers health conditions, allergies, and dietary preferences.
# Datasets used:
1. https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
2. https://www.kaggle.com/datasets/dikshaasinghhh/bajaj
# Milestone 1: Data Collection and Preprocessing
-	Collect sample medical reports (PDF, text, scanned images).
-	Implement OCR for scanned reports and text extraction.
-	Milestone: Successfully extract structured numeric and textual data from sample reports.
## Tasks:
-	Medical Report Input: Accepts PDF, image, or text-based reports uploaded by the user.
-	Data Extraction Module: Uses OCR and parsing techniques to extract structured numerical and textual data.
-	ML Analysis of Numeric Data: Evaluates blood test and health metrics to identify potential risks.
# Milestone 2: ML-Based Health Analysis
-	Train ML models to classify health conditions from numeric lab results.
-	Implement thresholds and alerts for abnormal values.
-	Milestone: ML model achieves 85% accuracy in detecting critical conditions.
## Tasks:
- Dataset Loading
-	Feature Selection
-	Data Splitting
-	Model Training
-	Model Evaluation
-	Threshold Definition
-	Alert Generation
# Milestone 3: NLP/AI Text Interpretation
-	Integrate GPT/BERT for interpreting doctor notes and prescriptions.
-	Map textual instructions to actionable diet guidelines.
-	Milestone: Convert at least 80% of textual notes into actionable diet rules.
## Tasks:
-	Prescription Text Input: Accepts doctor prescriptions and medical notes directly in text format.
-	Text Preprocessing: Cleans and normalizes the prescription text for better NLP understanding.
-	NLP-Based Text Representation: Converts prescription text into numerical representations using BERT-based models.
-	Medical Context Interpretation: Analyzes the text to understand medical meaning and intent.
-	Medical Condition Identification: Identifies diseases and health conditions mentioned in the prescription.
-	Diet Rule Mapping: Maps identified medical conditions to predefined diet recommendations and restrictions.
-	Structured Diet Output Generation: Generates clear and actionable diet guidelines in structured format.

