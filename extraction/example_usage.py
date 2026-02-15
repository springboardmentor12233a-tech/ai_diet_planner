"""
Example usage of the DataExtractor class.

This script demonstrates how to use the DataExtractor to extract health metrics
and textual notes from medical report text.
"""

from ai_diet_planner.extraction.data_extractor import DataExtractor, InsufficientDataError


def main():
    """Demonstrate DataExtractor usage with sample medical report text."""
    
    # Create an instance of DataExtractor
    extractor = DataExtractor()
    
    # Sample medical report text
    sample_report = """
    MEDICAL LABORATORY REPORT
    Patient ID: 12345
    Date: 2024-01-15
    
    Laboratory Results:
    
    Glucose (Fasting): 126 mg/dL
    Total Cholesterol: 240 mg/dL
    LDL Cholesterol: 160 mg/dL
    HDL Cholesterol: 38 mg/dL
    Triglycerides: 200 mg/dL
    BMI: 32.5
    Blood Pressure: 145/95 mmHg
    Hemoglobin: 12.5 g/dL
    HbA1c: 7.2%
    
    Doctor's Notes:
    Patient shows elevated glucose levels consistent with diabetes.
    Blood pressure is in hypertension stage 2 range.
    Cholesterol levels are concerning, particularly LDL.
    
    Recommendations:
    - Start diabetes management program
    - Reduce sodium intake to <2000mg/day
    - Increase physical activity to 30 minutes daily
    - Follow up in 3 months for re-evaluation
    
    Prescriptions:
    1. Metformin 500mg - Take twice daily with meals
    2. Lisinopril 10mg - Take once daily in the morning
    3. Atorvastatin 20mg - Take once daily at bedtime
    """
    
    print("=" * 70)
    print("DataExtractor Example Usage")
    print("=" * 70)
    print()
    
    # Extract structured health metrics
    print("1. Extracting Structured Health Metrics:")
    print("-" * 70)
    try:
        structured_data = extractor.extract_structured_data(sample_report, "REPORT-001")
        
        print(f"Report ID: {structured_data.report_id}")
        print(f"Extraction Time: {structured_data.extraction_timestamp}")
        print(f"Total Metrics Extracted: {len(structured_data.metrics)}")
        print()
        
        for metric in structured_data.metrics:
            print(f"  • {metric.metric_type.value:25s}: {metric.value:8.2f} {metric.unit:10s} "
                  f"(confidence: {metric.confidence:.2f})")
    
    except InsufficientDataError as e:
        print(f"Error: {e}")
    
    print()
    
    # Extract textual notes
    print("2. Extracting Textual Notes:")
    print("-" * 70)
    textual_notes = extractor.extract_textual_notes(sample_report)
    
    for i, note in enumerate(textual_notes, 1):
        print(f"\nNote {i} - Section: {note.section}")
        print(f"Content preview: {note.content[:100]}...")
    
    print()
    print()
    
    # Extract with ambiguity flagging
    print("3. Extraction with Ambiguity Flagging:")
    print("-" * 70)
    result = extractor.extract_with_ambiguity_flagging(sample_report, "REPORT-001")
    
    print(f"Structured Metrics: {len(result.structured_data.metrics)}")
    print(f"Textual Notes: {len(result.textual_notes)}")
    print(f"Ambiguous Values Flagged: {len(result.ambiguous_values)}")
    
    if result.ambiguous_values:
        print("\nAmbiguous values requiring review:")
        for amb in result.ambiguous_values[:3]:  # Show first 3
            print(f"  • Value: {amb['value']}, Possible types: {amb['possible_types']}")
    
    print()
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
