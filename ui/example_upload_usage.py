"""
Example usage of the Upload page with backend integration.

This demonstrates how the Upload page processes medical reports through
the complete AI NutriCare pipeline.
"""

from pathlib import Path
from ai_diet_planner.main import AINutriCareOrchestrator
from ai_diet_planner.processor.report_processor import UploadedFile
from ai_diet_planner.models import PatientProfile, UserPreferences


def example_upload_and_process():
    """
    Example: Upload a medical report and process it through the pipeline.
    """
    print("=== AI NutriCare Upload Example ===\n")
    
    # Initialize orchestrator
    print("1. Initializing AI NutriCare Orchestrator...")
    orchestrator = AINutriCareOrchestrator(
        ocr_backend="tesseract",
        nlp_model="bert"
    )
    
    # Create sample medical report content
    print("2. Creating sample medical report...")
    sample_report = """
    MEDICAL LABORATORY REPORT
    
    Patient: John Doe
    Date: 2024-01-15
    
    LAB RESULTS:
    - Glucose (Fasting): 126 mg/dL
    - Total Cholesterol: 240 mg/dL
    - LDL Cholesterol: 160 mg/dL
    - HDL Cholesterol: 35 mg/dL
    - Triglycerides: 200 mg/dL
    - Blood Pressure: 145/95 mmHg
    - BMI: 32.5
    - Hemoglobin: 13.5 g/dL
    
    DOCTOR'S NOTES:
    Patient shows signs of prediabetes and hypertension.
    Recommend low-sodium diet and reduced sugar intake.
    Increase fiber consumption and regular exercise.
    Avoid processed foods and saturated fats.
    """
    
    # Create UploadedFile object
    uploaded_file = UploadedFile(
        filename="sample_report.txt",
        content=sample_report.encode('utf-8')
    )
    
    # Create patient profile
    print("3. Creating patient profile...")
    user_preferences = UserPreferences(
        dietary_style="Mediterranean",
        allergies=["shellfish"],
        dislikes=["liver"],
        cultural_preferences=[]
    )
    
    patient_profile = PatientProfile(
        patient_id="",
        age=45,
        gender="Male",
        height_cm=175,
        weight_kg=95,
        activity_level="light",
        preferences=user_preferences,
        created_at=None
    )
    
    # Process report
    print("4. Processing medical report through pipeline...")
    print("   - Extracting text...")
    print("   - Analyzing health metrics...")
    print("   - Interpreting doctor notes...")
    print("   - Generating diet plan...")
    
    result = orchestrator.process_report(
        uploaded_file=uploaded_file,
        patient_profile=patient_profile,
        user_preferences=user_preferences,
        export_pdf=True,
        export_json=True
    )
    
    # Display results
    print(f"\n5. Processing Results:")
    print(f"   Status: {result.status.value}")
    print(f"   Processing Time: {result.processing_time:.2f}s")
    
    if result.status.value == "completed":
        print(f"\n   ✓ Health Metrics Extracted: {len(result.structured_data.metrics) if result.structured_data else 0}")
        
        if result.structured_data:
            print("\n   Extracted Metrics:")
            for metric in result.structured_data.metrics:
                print(f"     - {metric.metric_type.value}: {metric.value} {metric.unit}")
        
        print(f"\n   ✓ Health Conditions Detected: {len(result.health_conditions)}")
        for condition in result.health_conditions:
            print(f"     - {condition.condition_type.value} (confidence: {condition.confidence:.2%})")
        
        print(f"\n   ✓ Health Alerts: {len(result.alerts)}")
        for alert in result.alerts:
            print(f"     - {alert.severity.value.upper()}: {alert.message}")
        
        print(f"\n   ✓ Diet Rules Extracted: {len(result.diet_rules)}")
        for rule in result.diet_rules[:3]:  # Show first 3
            print(f"     - {rule.priority.value}: {rule.rule_text}")
        
        if result.diet_plan:
            print(f"\n   ✓ Diet Plan Generated:")
            print(f"     - Daily Calories: {result.diet_plan.daily_calories:.0f}")
            print(f"     - Meals: {len(result.diet_plan.meals)}")
            print(f"     - Macros: {result.diet_plan.macronutrient_targets.protein_percent:.0f}% protein, "
                  f"{result.diet_plan.macronutrient_targets.carbs_percent:.0f}% carbs, "
                  f"{result.diet_plan.macronutrient_targets.fat_percent:.0f}% fat")
        
        if result.pdf_export:
            print(f"\n   ✓ PDF Export: {len(result.pdf_export)} bytes")
        
        if result.json_export:
            print(f"   ✓ JSON Export: {len(result.json_export)} characters")
    else:
        print(f"\n   ✗ Processing Failed: {result.error_message}")
    
    print("\n=== Upload Example Complete ===")


def example_file_validation():
    """
    Example: Validate file size and format before processing.
    """
    print("\n=== File Validation Example ===\n")
    
    # Test file size validation
    print("1. Testing file size validation...")
    
    # Create a file that's too large (> 10MB)
    large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
    file_size_mb = len(large_content) / (1024 * 1024)
    
    if file_size_mb > 10:
        print(f"   ✗ File size {file_size_mb:.2f} MB exceeds 10 MB limit")
    else:
        print(f"   ✓ File size {file_size_mb:.2f} MB is within limit")
    
    # Test supported formats
    print("\n2. Testing supported file formats...")
    supported_formats = ["pdf", "jpg", "jpeg", "png", "tif", "tiff", "txt"]
    test_files = ["report.pdf", "scan.jpg", "results.png", "data.txt", "document.docx"]
    
    for filename in test_files:
        extension = filename.split(".")[-1].lower()
        if extension in supported_formats:
            print(f"   ✓ {filename} - Supported format")
        else:
            print(f"   ✗ {filename} - Unsupported format")
    
    print("\n=== Validation Example Complete ===")


def example_error_handling():
    """
    Example: Handle errors during report processing.
    """
    print("\n=== Error Handling Example ===\n")
    
    # Initialize orchestrator
    orchestrator = AINutriCareOrchestrator()
    
    # Create invalid report (no health metrics)
    print("1. Processing report with no health metrics...")
    invalid_report = "This is just plain text with no medical data."
    
    uploaded_file = UploadedFile(
        filename="invalid_report.txt",
        content=invalid_report.encode('utf-8')
    )
    
    result = orchestrator.process_report(
        uploaded_file=uploaded_file,
        patient_profile=None,
        user_preferences=None,
        export_pdf=False,
        export_json=False
    )
    
    if result.status.value == "failed":
        print(f"   ✗ Processing failed as expected: {result.error_message}")
        print("\n   Troubleshooting steps:")
        print("   1. Ensure the document contains health metrics")
        print("   2. Try uploading a higher quality scan")
        print("   3. Verify the file format is supported")
    
    print("\n=== Error Handling Example Complete ===")


if __name__ == "__main__":
    # Run examples
    example_upload_and_process()
    example_file_validation()
    example_error_handling()
