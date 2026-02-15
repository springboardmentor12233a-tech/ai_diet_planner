"""
Example usage of the DataStore with encryption and security features.

This script demonstrates:
1. Setting up encryption
2. Saving patient data with encrypted sensitive fields
3. Retrieving patient data
4. Saving diet plans
5. Viewing audit logs
6. Deleting patient data
"""

import os
from datetime import datetime
from pathlib import Path

from .data_store import DataStore
from ..models.patient_data import PatientProfile, UserPreferences
from ..models.diet_data import (
    DietPlan, Meal, MacronutrientRatios, 
    DietaryRestriction, Food, Portion
)
from ..models.enums import MealType


def setup_encryption_key():
    """Set up encryption key for demonstration."""
    # In production, this would come from a secure key management service
    os.environ['NUTRICARE_ENCRYPTION_KEY'] = 'demo-encryption-key-change-in-production'
    print("✓ Encryption key configured")


def create_sample_patient():
    """Create a sample patient profile."""
    preferences = UserPreferences(
        dietary_style="vegetarian",
        allergies=["peanuts", "shellfish"],
        dislikes=["mushrooms", "olives"],
        cultural_preferences=["halal"]
    )
    
    patient = PatientProfile(
        patient_id="patient-demo-001",
        age=35,
        gender="female",
        height_cm=165.0,
        weight_kg=68.0,
        activity_level="moderate",
        preferences=preferences,
        created_at=datetime.now()
    )
    
    return patient


def create_sample_diet_plan():
    """Create a sample diet plan."""
    # Create macronutrient targets
    macros = MacronutrientRatios(
        protein_percent=30.0,
        carbs_percent=40.0,
        fat_percent=30.0
    )
    
    # Create a sample food item
    oatmeal = Food(
        name="Oatmeal",
        calories=150.0,
        protein_g=5.0,
        carbs_g=27.0,
        fat_g=3.0,
        fiber_g=4.0,
        sodium_mg=0.0,
        sugar_g=1.0,
        category="grains",
        fdc_id="173904"
    )
    
    # Create a portion
    portion = Portion(
        food=oatmeal,
        amount=50.0,
        unit="g",
        calories=150.0,
        protein_g=5.0,
        carbs_g=27.0,
        fat_g=3.0
    )
    
    # Create a meal
    breakfast = Meal(
        meal_type=MealType.BREAKFAST,
        portions=[portion],
        total_calories=500.0,
        total_protein_g=25.0,
        total_carbs_g=50.0,
        total_fat_g=17.0
    )
    
    # Create dietary restriction
    restriction = DietaryRestriction(
        restriction_type="allergy",
        restricted_items=["peanuts", "shellfish"],
        severity="strict"
    )
    
    # Create diet plan
    plan = DietPlan(
        plan_id="plan-demo-001",
        patient_id="patient-demo-001",
        generated_at=datetime.now(),
        daily_calories=2000.0,
        macronutrient_targets=macros,
        meals=[breakfast],
        restrictions=[restriction],
        recommendations=[
            "Drink at least 8 glasses of water daily",
            "Include variety of colorful vegetables",
            "Limit processed foods"
        ],
        health_conditions=[]
    )
    
    return plan


def demonstrate_encryption():
    """Demonstrate encryption functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Encryption and Decryption")
    print("="*60)
    
    from .data_store import EncryptionManager
    
    # Create encryption manager
    key = b'0' * 32  # 32-byte key for demo
    manager = EncryptionManager(key)
    
    # Encrypt sensitive data
    sensitive_data = "Patient Name: Jane Doe, DOB: 1988-05-15"
    print(f"\nOriginal data: {sensitive_data}")
    
    encrypted = manager.encrypt(sensitive_data)
    print(f"Encrypted data: {encrypted[:50]}...")
    
    decrypted = manager.decrypt(encrypted)
    print(f"Decrypted data: {decrypted}")
    
    print("\n✓ Encryption/decryption successful")


def demonstrate_data_store():
    """Demonstrate DataStore functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATION: Secure Data Storage")
    print("="*60)
    
    # Initialize data store
    db_path = "demo_nutricare.db"
    data_store = DataStore(db_path=db_path)
    print(f"\n✓ DataStore initialized at {db_path}")
    
    # Create sample data
    patient = create_sample_patient()
    diet_plan = create_sample_diet_plan()
    
    # Save patient with encrypted sensitive data
    print("\n1. Saving patient with encrypted sensitive fields...")
    patient_id = data_store.save_patient(
        patient,
        user_id="doctor-demo-001",
        name="Jane Doe",  # This will be encrypted
        dob="1988-05-15"  # This will be encrypted
    )
    print(f"   ✓ Patient saved with ID: {patient_id}")
    
    # Retrieve patient
    print("\n2. Retrieving patient data...")
    retrieved_patient = data_store.get_patient(
        patient_id,
        user_id="doctor-demo-001"
    )
    print(f"   ✓ Patient retrieved: {retrieved_patient.patient_id}")
    print(f"   - Age: {retrieved_patient.age}")
    print(f"   - Gender: {retrieved_patient.gender}")
    print(f"   - Dietary style: {retrieved_patient.preferences.dietary_style}")
    print(f"   - Allergies: {', '.join(retrieved_patient.preferences.allergies)}")
    
    # Save diet plan
    print("\n3. Saving diet plan...")
    plan_id = data_store.save_diet_plan(
        patient_id,
        diet_plan,
        user_id="doctor-demo-001"
    )
    print(f"   ✓ Diet plan saved with ID: {plan_id}")
    
    # Get patient history
    print("\n4. Retrieving patient history...")
    history = data_store.get_patient_history(
        patient_id,
        user_id="doctor-demo-001"
    )
    print(f"   ✓ Medical reports: {len(history['reports'])}")
    print(f"   ✓ Diet plans: {len(history['plans'])}")
    
    # Check for duplicates
    print("\n5. Checking for duplicate patients...")
    is_duplicate = data_store.check_duplicate_patient(patient_id)
    print(f"   ✓ Patient exists: {is_duplicate}")
    
    # Try to save duplicate patient (should fail)
    print("\n6. Testing duplicate prevention...")
    try:
        data_store.save_patient(
            patient,
            user_id="doctor-demo-001",
            name="Jane Doe"
        )
        print("   ✗ Duplicate prevention failed!")
    except ValueError as e:
        print(f"   ✓ Duplicate prevented: {str(e)[:60]}...")
    
    # Use get_or_create_patient
    print("\n7. Using get_or_create_patient...")
    patient_id_2, created = data_store.get_or_create_patient(
        patient,
        user_id="doctor-demo-001",
        name="Jane Doe"
    )
    print(f"   ✓ Patient ID: {patient_id_2}, Created: {created}")
    
    # View audit logs
    print("\n8. Viewing audit logs...")
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            SELECT timestamp, user_id, action, resource_type, resource_id
            FROM audit_log
            ORDER BY id
        """)
        print("\n   Audit Log Entries:")
        print("   " + "-"*70)
        for row in cursor.fetchall():
            timestamp, user_id, action, resource_type, resource_id = row
            print(f"   {timestamp[:19]} | {user_id:20} | {action:8} | {resource_type:15} | {resource_id}")
    
    # Verify encryption in database
    print("\n9. Verifying data encryption in database...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            SELECT encrypted_name, encrypted_dob
            FROM patients
            WHERE id = ?
        """, (patient_id,))
        row = cursor.fetchone()
        encrypted_name, encrypted_dob = row
        
        print(f"   Encrypted name (first 50 chars): {encrypted_name[:50]}...")
        print(f"   Encrypted DOB (first 50 chars): {encrypted_dob[:50]}...")
        print("   ✓ Sensitive data is encrypted in database")
    
    # Delete patient data with verification
    print("\n10. Deleting patient data with verification (GDPR compliance)...")
    result = data_store.delete_patient_data(
        patient_id,
        user_id="doctor-demo-001",
        verify=True
    )
    print(f"   ✓ Deletion successful: {result['success']}")
    print(f"   ✓ Records deleted:")
    for record_type, count in result['deleted_records'].items():
        if count > 0:
            print(f"      - {record_type}: {count}")
    print(f"   ✓ Verification complete: {result['verification']['complete']}")
    print(f"   ✓ Remaining records: {result['verification']['total_remaining']}")
    
    # Verify deletion
    retrieved_after_delete = data_store.get_patient(patient_id)
    print(f"   ✓ Patient after deletion: {retrieved_after_delete}")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    
    # Cleanup
    print(f"\nCleaning up demo database: {db_path}")
    import time
    import gc
    gc.collect()  # Force garbage collection to release file handles
    time.sleep(0.1)  # Small delay for Windows file locking
    try:
        os.unlink(db_path)
        print("✓ Demo database removed")
    except PermissionError:
        print("⚠ Demo database still in use, will be cleaned up later")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("AI NutriCare System - Data Store Security Demo")
    print("="*60)
    
    # Setup
    setup_encryption_key()
    
    # Run demonstrations
    demonstrate_encryption()
    demonstrate_data_store()
    
    # Cleanup
    if 'NUTRICARE_ENCRYPTION_KEY' in os.environ:
        del os.environ['NUTRICARE_ENCRYPTION_KEY']
    
    print("\n✓ All demonstrations completed successfully!")


if __name__ == "__main__":
    main()
