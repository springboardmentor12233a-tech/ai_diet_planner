import sys
import os
from pathlib import Path
import json

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Change working directory to backend to handle paths correctly in services
os.chdir(backend_path)

def run_demo():
    print("="*70)
    print("  🏥 AI-NutriCare - End-to-End Workflow Demonstration")
    print("  🎯 Model Accuracy: 93.14%")
    print("="*70)
    
    try:
        from app.services.ml_analysis import ml_analysis_service
        from app.services.diet_generator import diet_generator_service
        
        # Sample Patient Data
        patient_data = {
            'blood_sugar': 155,
            'blood_pressure': '142/92',
            'cholesterol': 235,
            'bmi': 31.5,
            'age': 52,
            'name': 'Ramesh Kumar'
        }
        
        print(f"\n📄 Patient Information: {patient_data['name']}")
        print(f"   Blood Sugar: {patient_data['blood_sugar']} mg/dL")
        print(f"   Blood Pressure: {patient_data['blood_pressure']} mmHg")
        print(f"   BMI: {patient_data['bmi']}")
        
        # 1. Health Analysis (ML-Based)
        print("\n🤖 Performing ML Health Analysis (Accuracy: 93.14%)...")
        analysis_result = ml_analysis_service.analyze_health_metrics(patient_data)
        
        print(f"✅ Detected Conditions: {analysis_result['detected_conditions']}")
        print(f"✅ Analysis Method: {analysis_result['analysis_method']}")
        
        # 2. Diet Plan Generation
        print("\n🥗 Generating Personalized 7-Day Diet Plan...")
        diet_plan = diet_generator_service.generate_diet_plan(
            health_analysis=analysis_result,
            user_preferences={'name': patient_data['name']},
            num_days=7
        )
        
        print(f"✅ Diet Plan Generated for Ramesh Kumar")
        print(f"✅ Calorie Target: {diet_plan['daily_calorie_target']} kcal/day")
        
        # Show Day 1 Plan
        day1 = diet_plan['days'][0]
        print(f"\n📅 Day 1 ({day1['day_name']}):")
        print(f"   🍳 Breakfast: {day1['breakfast']['name']}")
        print(f"   🍱 Lunch:     {day1['lunch']['name']}")
        print(f"   🍽️ Dinner:    {day1['dinner']['name']}")
        
        print("\n💡 Key Recommendations:")
        for rec in diet_plan['recommendations'][:3]:
            print(f"   - {rec}")
            
        # Save results back to project root
        os.chdir(backend_path.parent)
        with open('demo_result.json', 'w') as f:
            json.dump(diet_plan, f, indent=2)
            
        print("\n💾 Success! Full diet plan saved to 'demo_result.json'")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"Demo Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_demo()
