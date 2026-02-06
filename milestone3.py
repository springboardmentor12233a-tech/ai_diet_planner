# milestone3.py
# Main runner for Milestone 3

from M3_sampletext import prescription_text
from M3_text_analyzer import analyze_prescription

# Analyze the prescription text
analysis_result = analyze_prescription(prescription_text)

print(" DIET INSTRUCTIONS FROM PRESCRIPTION \n")

print("Foods to LIMIT:")
for item in analysis_result["limit"]:
    print("-", item)

print("\nFoods to INCREASE:")
for item in analysis_result["increase"]:
    print("-", item)