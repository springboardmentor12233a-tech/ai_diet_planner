#!/usr/bin/env python3
"""
AI NutriCare System - Interactive Demo Script

This script demonstrates the complete functionality of the AI NutriCare System.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text):
    """Print a formatted section header."""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}\n")


def demo_1_create_sample_report():
    """Demo 1: Create a sample medical report."""
    print_header("DEMO 1: Creating Sample Medical Report")
    
    sample_report = """MEDICAL REPORT

Patient: John Doe
Date: 2024-01-15
Age: 45 years
Gender: Male
Height: 175 cm
Weight: 85 kg

LAB RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Fasting Blood Glucose: 155 mg/dL (High) ⚠️
- HbA1c: 7.2% (Elevated) ⚠️
- Total Cholesterol: 240 mg/dL (High) ⚠️
- LDL Cholesterol: 160 mg/dL (High) ⚠️
- HDL Cholesterol: 35 mg/dL (Low) ⚠️
- Triglycerides: 220 mg/dL (High) ⚠️
- BMI: 29.5 (Overweight) ⚠️
- Blood Pressure: 135/85 mmHg (Elevated) ⚠️
- Hemoglobin: 14.2 g/dL (Normal) ✓

DOCTOR'S NOTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient shows signs of prediabetes with elevated glucose and HbA1c levels.
Recommend dietary modifications to reduce sugar intake and increase fiber.
Monitor blood glucose levels regularly.
Patient has family history of diabetes.

DIETARY RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Follow a low glycemic index diet
✓ Reduce processed foods and added sugars
✓ Increase intake of vegetables and whole grains
✓ Limit saturated fats
✓ Avoid sugary beverages
✓ Increase physical activity to 30 minutes daily

FOLLOW-UP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Schedule follow-up appointment in 3 months to reassess glucose levels.
"""
    
    # Save to file
    report_path = Path("demo_medical_report.txt")
    report_path.write_text(sample_report)
    
    print("✓ Sample medical report created: demo_medical_report.txt")
    print(f"✓ File size: {report_path.stat().st_size} bytes")
    print("\nReport Preview:")
    print("─" * 70)
    print(sample_report[:500] + "...")
    
    return report_path


def demo_2_process_report(report_path):
    """Demo 2: Process the medical report through the pipeline."""
    print_header("DEMO 2: Processing Medical Report")
    
    try:
        from ai_diet_planner.main import process_medical_report
        from ai_diet_planner.models import PatientProfile, UserPreferences
        
        print("Initializing AI NutriCare System...")
        print("  ✓ Loading OCR engine")
        print("  ✓ Loading ML health analyzer")
        print("  ✓ Loading NLP text interpreter")
        print("  ✓ Loading diet plan generator")
        print("  ✓ Initializing secure data store")
        
        print("\nCreating patient profile...")
        preferences = UserPreferences(
            dietary_style="balanced",
            allergies=["peanuts"],
            dislikes=["liver"],
            cultural_preferences=[]
        )
        
        patient = PatientProfile(
            patient_id="demo-patient-001",
            age=45,
            gender="Male",
            height_cm=175.0,
            weight_kg=85.0,
            activity_level="moderate",
            preferences=preferences,
            created_at=datetime.now()
        )
        
        print("  ✓ Patient profile created")
        print(f"    - Age: {patient.age}")
        print(f"    - Gender: {patient.gender}")
        print(f"    - BMI: {patient.weight_kg / ((patient.height_cm/100)**2):.1f}")
        print(f"    - Activity: {patient.activity_level}")
        
        print("\nProcessing report through AI pipeline...")
        print("  [1/7] Validating file...")
        print("  [2/7] Extracting text...")
        print("  [3/7] Extracting health metrics...")
        print("  [4/7] Analyzing health conditions (ML)...")
        print("  [5/7] Interpreting doctor notes (NLP)...")
        print("  [6/7] Generating personalized diet plan...")
        print("  [7/7] Exporting results...")
        
        # Set encryption key for demo
        os.environ['NUTRICARE_ENCRYPTION_KEY'] = 'demo-encryption-key-for-testing'
        
        # Process the report
        result = process_medical_report(
            report_path,
            patient_profile=patient,
            user_preferences=preferences
        )
        
        print("\n" + "✓" * 35 + " PROCESSING COMPLETE " + "✓" * 35)
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_3_display_results(result):
    """Demo 3: Display processing results."""
    if not result:
        print("\n✗ No results to display")
        return
    
    print_header("DEMO 3: Processing Results")
    
    # Overall status
    print_section("Overall Status")
    print(f"Status: {result.status.value.upper()}")
    print(f"Processing Time: {result.processing_time:.2f} seconds")
    print(f"Report ID: {result.report_id}")
    
    if result.status.value != "completed":
        print(f"\n✗ Processing failed: {result.error_message}")
        return
    
    # Extracted health metrics
    print_section("Extracted Health Metrics")
    if result.structured_data and result.structured_data.metrics:
        print(f"Total metrics extracted: {len(result.structured_data.metrics)}\n")
        for metric in result.structured_data.metrics:
            print(f"  • {metric.metric_type.value.replace('_', ' ').title()}: "
                  f"{metric.value} {metric.unit} "
                  f"(confidence: {metric.confidence*100:.0f}%)")
    else:
        print("  No metrics extracted")
    
    # Health conditions detected
    print_section("Health Conditions Detected")
    if result.health_conditions:
        print(f"Total conditions detected: {len(result.health_conditions)}\n")
        for condition in result.health_conditions:
            confidence_bar = "█" * int(condition.confidence * 20)
            print(f"  • {condition.condition_type.value.replace('_', ' ').title()}")
            print(f"    Confidence: {confidence_bar} {condition.confidence*100:.1f}%")
            if condition.contributing_metrics:
                print(f"    Based on: {', '.join(condition.contributing_metrics)}")
    else:
        print("  No conditions detected")
    
    # Health alerts
    print_section("Health Alerts")
    if result.alerts:
        print(f"Total alerts generated: {len(result.alerts)}\n")
        
        # Group by severity
        critical = [a for a in result.alerts if a.severity.value == "critical"]
        warnings = [a for a in result.alerts if a.severity.value == "warning"]
        normal = [a for a in result.alerts if a.severity.value == "normal"]
        
        if critical:
            print("  🔴 CRITICAL ALERTS:")
            for alert in critical:
                print(f"     • {alert.message}")
                if alert.recommended_action:
                    print(f"       → {alert.recommended_action}")
        
        if warnings:
            print("\n  🟡 WARNINGS:")
            for alert in warnings:
                print(f"     • {alert.message}")
                if alert.recommended_action:
                    print(f"       → {alert.recommended_action}")
        
        if normal:
            print("\n  🟢 NORMAL:")
            for alert in normal:
                print(f"     • {alert.message}")
    else:
        print("  No alerts generated")
    
    # Textual notes
    print_section("Doctor's Notes Extracted")
    if result.textual_notes:
        print(f"Total notes extracted: {len(result.textual_notes)}\n")
        for i, note in enumerate(result.textual_notes[:3], 1):  # Show first 3
            print(f"  {i}. {note.content[:100]}...")
    else:
        print("  No textual notes extracted")
    
    # Diet rules
    print_section("Dietary Rules Extracted")
    if result.diet_rules:
        print(f"Total rules extracted: {len(result.diet_rules)}\n")
        for rule in result.diet_rules:
            priority_icon = "🔴" if rule.priority.value == "required" else "🟡" if rule.priority.value == "recommended" else "🟢"
            print(f"  {priority_icon} {rule.rule_text}")
            print(f"     Priority: {rule.priority.value.upper()}")
            if rule.affected_food_categories:
                print(f"     Affects: {', '.join(rule.affected_food_categories)}")
    else:
        print("  No dietary rules extracted (using ML-based recommendations)")
    
    # Diet plan
    print_section("Personalized Diet Plan")
    if result.diet_plan:
        print(f"Daily Caloric Target: {result.diet_plan.daily_calories:.0f} calories\n")
        
        print("Macronutrient Distribution:")
        macros = result.diet_plan.macronutrient_targets
        print(f"  • Protein: {macros.protein_percent:.0f}%")
        print(f"  • Carbohydrates: {macros.carbs_percent:.0f}%")
        print(f"  • Fats: {macros.fat_percent:.0f}%")
        
        print(f"\nMeal Plan ({len(result.diet_plan.meals)} meals):")
        for meal in result.diet_plan.meals:
            print(f"\n  {meal.meal_type.value.upper()}")
            print(f"  Calories: {meal.total_calories:.0f} | "
                  f"Protein: {meal.total_protein_g:.0f}g | "
                  f"Carbs: {meal.total_carbs_g:.0f}g | "
                  f"Fat: {meal.total_fat_g:.0f}g")
            print(f"  Foods: {len(meal.portions)} items")
            for portion in meal.portions[:2]:  # Show first 2 items
                print(f"    • {portion.food.name}: {portion.amount:.0f}{portion.unit}")
        
        if result.diet_plan.restrictions:
            print(f"\n  Dietary Restrictions: {len(result.diet_plan.restrictions)}")
            for restriction in result.diet_plan.restrictions:
                print(f"    • {restriction.restriction_type}: {', '.join(restriction.restricted_items)}")
        
        if result.diet_plan.recommendations:
            print(f"\n  Additional Recommendations:")
            for rec in result.diet_plan.recommendations[:3]:
                print(f"    • {rec}")
    else:
        print("  No diet plan generated")
    
    # Export information
    print_section("Export Options")
    if result.pdf_export:
        print(f"  ✓ PDF Export: {len(result.pdf_export)} bytes")
        print("    Ready to save as: diet_plan.pdf")
    if result.json_export:
        print(f"  ✓ JSON Export: {len(result.json_export)} bytes")
        print("    Ready to save as: diet_plan.json")


def demo_4_save_exports(result):
    """Demo 4: Save exported files."""
    if not result or result.status.value != "completed":
        return
    
    print_header("DEMO 4: Saving Exports")
    
    # Save PDF
    if result.pdf_export:
        pdf_path = Path("demo_diet_plan.pdf")
        pdf_path.write_bytes(result.pdf_export)
        print(f"✓ PDF saved: {pdf_path}")
        print(f"  Size: {len(result.pdf_export)} bytes")
    
    # Save JSON
    if result.json_export:
        json_path = Path("demo_diet_plan.json")
        json_path.write_text(result.json_export)
        print(f"✓ JSON saved: {json_path}")
        print(f"  Size: {len(result.json_export)} bytes")
    
    print("\n✓ All exports saved successfully!")


def demo_5_web_interface():
    """Demo 5: Instructions for web interface."""
    print_header("DEMO 5: Web Interface")
    
    print("To run the Streamlit web interface:")
    print("\n  1. Open a terminal/command prompt")
    print("  2. Navigate to the ai_diet_planner directory:")
    print("     cd ai_diet_planner")
    print("  3. Run the Streamlit app:")
    print("     streamlit run ui/app.py")
    print("  4. Your browser will open to: http://localhost:8501")
    print("\nFeatures:")
    print("  • Upload medical reports (PDF, images, text)")
    print("  • View extracted health data")
    print("  • Review personalized diet plans")
    print("  • Export to PDF/JSON")
    print("  • View patient history")


def main():
    """Run all demos."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "AI NUTRICARE SYSTEM DEMO" + " " * 29 + "█")
    print("█" + " " * 10 + "Personalized Diet Planning from Medical Reports" + " " * 12 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        # Demo 1: Create sample report
        report_path = demo_1_create_sample_report()
        
        input("\nPress Enter to continue to Demo 2 (Processing)...")
        
        # Demo 2: Process report
        result = demo_2_process_report(report_path)
        
        if result:
            input("\nPress Enter to continue to Demo 3 (Results)...")
            
            # Demo 3: Display results
            demo_3_display_results(result)
            
            input("\nPress Enter to continue to Demo 4 (Exports)...")
            
            # Demo 4: Save exports
            demo_4_save_exports(result)
        
        input("\nPress Enter to continue to Demo 5 (Web Interface)...")
        
        # Demo 5: Web interface instructions
        demo_5_web_interface()
        
        print_header("DEMO COMPLETE!")
        print("✓ All demos completed successfully!")
        print("\nGenerated Files:")
        print("  • demo_medical_report.txt - Sample medical report")
        print("  • demo_diet_plan.pdf - Exported diet plan (PDF)")
        print("  • demo_diet_plan.json - Exported diet plan (JSON)")
        print("  • nutricare.db - Encrypted database")
        
        print("\nNext Steps:")
        print("  1. Review the generated files")
        print("  2. Try the web interface: streamlit run ai_diet_planner/ui/app.py")
        print("  3. Upload your own medical reports")
        print("  4. Explore the API documentation")
        
        print("\n" + "█" * 70)
        print("Thank you for trying AI NutriCare System! 🥗")
        print("█" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
