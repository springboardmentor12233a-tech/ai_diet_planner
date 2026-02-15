"""
Unit tests for the DataStore with encryption and security features.

Tests cover:
- Encryption/decryption functionality
- Patient data persistence
- Diet plan storage
- Audit logging
- Data deletion
- Duplicate prevention
"""

import os
import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path

from .data_store import DataStore, EncryptionManager, AuditLogger
from ..models.patient_data import PatientProfile, UserPreferences
from ..models.diet_data import DietPlan, Meal, MacronutrientRatios, DietaryRestriction
from ..models.enums import MealType


class TestEncryptionManager:
    """Test encryption and decryption functionality."""
    
    def test_encryption_with_provided_key(self):
        """Test encryption with a provided 32-byte key."""
        key = b'0' * 32  # 32-byte key
        manager = EncryptionManager(key)
        
        plaintext = "Sensitive patient data"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert encrypted != plaintext
        assert len(encrypted) > 0
    
    def test_encryption_with_env_var(self):
        """Test encryption using environment variable."""
        os.environ['NUTRICARE_ENCRYPTION_KEY'] = 'test-key-for-encryption'
        
        manager = EncryptionManager()
        plaintext = "Patient name: John Doe"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == plaintext
        
        del os.environ['NUTRICARE_ENCRYPTION_KEY']
    
    def test_encryption_without_key_raises_error(self):
        """Test that missing encryption key raises ValueError."""
        if 'NUTRICARE_ENCRYPTION_KEY' in os.environ:
            del os.environ['NUTRICARE_ENCRYPTION_KEY']
        
        with pytest.raises(ValueError, match="Encryption key not provided"):
            EncryptionManager()
    
    def test_encryption_empty_string(self):
        """Test encryption of empty string."""
        key = b'0' * 32
        manager = EncryptionManager(key)
        
        encrypted = manager.encrypt("")
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == ""
        assert encrypted == ""
    
    def test_encryption_unicode(self):
        """Test encryption of unicode characters."""
        key = b'0' * 32
        manager = EncryptionManager(key)
        
        plaintext = "Patient: José García 日本語"
        encrypted = manager.encrypt(plaintext)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encryption_different_each_time(self):
        """Test that encrypting the same plaintext produces different ciphertext (due to random IV)."""
        key = b'0' * 32
        manager = EncryptionManager(key)
        
        plaintext = "Same data"
        encrypted1 = manager.encrypt(plaintext)
        encrypted2 = manager.encrypt(plaintext)
        
        # Different ciphertext due to random IV
        assert encrypted1 != encrypted2
        
        # But both decrypt to same plaintext
        assert manager.decrypt(encrypted1) == plaintext
        assert manager.decrypt(encrypted2) == plaintext


class TestAuditLogger:
    """Test audit logging functionality."""
    
    def test_audit_log_creation(self):
        """Test that audit log table is created."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            logger = AuditLogger(db_path)
            
            # Verify table exists
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='audit_log'
                """)
                assert cursor.fetchone() is not None
        finally:
            import time
            import gc
            gc.collect()
            time.sleep(0.1)
            try:
                os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_audit_log_entry(self):
        """Test logging an audit entry."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            logger = AuditLogger(db_path)
            logger.log(
                action="CREATE",
                resource_type="patient",
                resource_id="patient-123",
                user_id="user-456",
                details={'field': 'value'},
                ip_address="192.168.1.1"
            )
            
            # Verify entry was logged
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT * FROM audit_log")
                row = cursor.fetchone()
                
                assert row is not None
                assert row[1] is not None  # timestamp
                assert row[2] == "user-456"  # user_id (column index 2)
                assert row[3] == "CREATE"  # action (column index 3)
                assert row[4] == "patient"  # resource_type (column index 4)
                assert row[5] == "patient-123"  # resource_id (column index 5)
                assert "field" in row[6]  # details (column index 6)
                assert row[7] == "192.168.1.1"  # ip_address (column index 7)
        finally:
            import time
            import gc
            gc.collect()  # Force garbage collection to release file handles
            time.sleep(0.1)  # Small delay for Windows file locking
            try:
                os.unlink(db_path)
            except PermissionError:
                pass  # Ignore if file is still locked


class TestDataStore:
    """Test DataStore functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Set encryption key
        os.environ['NUTRICARE_ENCRYPTION_KEY'] = 'test-encryption-key'
        
        yield db_path
        
        # Cleanup
        import time
        import gc
        gc.collect()  # Force garbage collection to release file handles
        time.sleep(0.1)  # Small delay for Windows file locking
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass  # Ignore if file is still locked
        if 'NUTRICARE_ENCRYPTION_KEY' in os.environ:
            del os.environ['NUTRICARE_ENCRYPTION_KEY']
    
    @pytest.fixture
    def data_store(self, temp_db):
        """Create a DataStore instance for testing."""
        return DataStore(db_path=temp_db)
    
    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient profile."""
        preferences = UserPreferences(
            dietary_style="vegetarian",
            allergies=["peanuts", "shellfish"],
            dislikes=["mushrooms"],
            cultural_preferences=["halal"]
        )
        
        return PatientProfile(
            patient_id="patient-001",
            age=35,
            gender="female",
            height_cm=165.0,
            weight_kg=68.0,
            activity_level="moderate",
            preferences=preferences,
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_diet_plan(self):
        """Create a sample diet plan."""
        macros = MacronutrientRatios(
            protein_percent=30.0,
            carbs_percent=40.0,
            fat_percent=30.0
        )
        
        meal = Meal(
            meal_type=MealType.BREAKFAST,
            portions=[],
            total_calories=500.0,
            total_protein_g=25.0,
            total_carbs_g=50.0,
            total_fat_g=17.0
        )
        
        restriction = DietaryRestriction(
            restriction_type="allergy",
            restricted_items=["peanuts"],
            severity="strict"
        )
        
        return DietPlan(
            plan_id="plan-001",
            patient_id="patient-001",
            generated_at=datetime.now(),
            daily_calories=2000.0,
            macronutrient_targets=macros,
            meals=[meal],
            restrictions=[restriction],
            recommendations=["Drink plenty of water"],
            health_conditions=[]
        )
    
    def test_database_initialization(self, data_store):
        """Test that database tables are created."""
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'patients' in tables
            assert 'medical_reports' in tables
            assert 'health_metrics' in tables
            assert 'diet_plans' in tables
            assert 'audit_log' in tables
    
    def test_database_indexes(self, data_store):
        """Test that performance indexes are created."""
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index'
                ORDER BY name
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Check for required indexes (Requirement 16.4)
            assert 'idx_patients_created' in indexes
            assert 'idx_reports_patient' in indexes
            assert 'idx_plans_patient' in indexes
    
    def test_save_patient(self, data_store, sample_patient):
        """Test saving a patient profile."""
        patient_id = data_store.save_patient(
            sample_patient,
            user_id="user-123",
            name="Jane Doe",
            dob="1988-05-15"
        )
        
        assert patient_id == "patient-001"
        
        # Verify patient was saved
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[0] == "patient-001"  # id
            assert len(row[1]) > 0  # encrypted_name
            assert len(row[2]) > 0  # encrypted_dob
            assert row[3] == 35  # age
    
    def test_get_patient(self, data_store, sample_patient):
        """Test retrieving a patient profile."""
        # Save patient first
        data_store.save_patient(
            sample_patient,
            name="Jane Doe",
            dob="1988-05-15"
        )
        
        # Retrieve patient
        retrieved = data_store.get_patient("patient-001", user_id="user-123")
        
        assert retrieved is not None
        assert retrieved.patient_id == "patient-001"
        assert retrieved.age == 35
        assert retrieved.gender == "female"
        assert retrieved.preferences.dietary_style == "vegetarian"
        assert "peanuts" in retrieved.preferences.allergies
    
    def test_get_nonexistent_patient(self, data_store):
        """Test retrieving a patient that doesn't exist."""
        retrieved = data_store.get_patient("nonexistent-id")
        assert retrieved is None
    
    def test_save_diet_plan(self, data_store, sample_patient, sample_diet_plan):
        """Test saving a diet plan."""
        # Save patient first
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Save diet plan
        plan_id = data_store.save_diet_plan(
            "patient-001",
            sample_diet_plan,
            user_id="user-123"
        )
        
        assert plan_id == "plan-001"
        
        # Verify plan was saved
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("SELECT * FROM diet_plans WHERE id = ?", (plan_id,))
            row = cursor.fetchone()
            
            assert row is not None
            assert row[0] == "plan-001"  # id
            assert row[1] == "patient-001"  # patient_id
            
            # Verify plan data is valid JSON
            plan_data = json.loads(row[2])
            assert plan_data['daily_calories'] == 2000.0
    
    def test_get_patient_history(self, data_store, sample_patient, sample_diet_plan):
        """Test retrieving patient history ordered by date."""
        # Save patient and diet plan
        data_store.save_patient(sample_patient, name="Jane Doe")
        data_store.save_diet_plan("patient-001", sample_diet_plan)
        
        # Get history
        history = data_store.get_patient_history("patient-001", user_id="user-123")
        
        assert 'reports' in history
        assert 'plans' in history
        assert len(history['plans']) == 1
        assert history['plans'][0]['id'] == "plan-001"
    
    def test_patient_history_ordering(self, data_store, sample_patient):
        """Test that patient history is ordered by date (most recent first)."""
        import time
        from ..models.diet_data import DietPlan, MacronutrientRatios, Meal
        from ..models.enums import MealType
        
        # Save patient
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Create multiple diet plans with different timestamps
        macros = MacronutrientRatios(
            protein_percent=30.0,
            carbs_percent=40.0,
            fat_percent=30.0
        )
        
        meal = Meal(
            meal_type=MealType.BREAKFAST,
            portions=[],
            total_calories=500.0,
            total_protein_g=25.0,
            total_carbs_g=50.0,
            total_fat_g=17.0
        )
        
        # Save first plan
        plan1 = DietPlan(
            plan_id="plan-001",
            patient_id="patient-001",
            generated_at=datetime(2024, 1, 1, 10, 0, 0),
            daily_calories=2000.0,
            macronutrient_targets=macros,
            meals=[meal],
            restrictions=[],
            recommendations=[],
            health_conditions=[]
        )
        data_store.save_diet_plan("patient-001", plan1)
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        # Save second plan (more recent)
        plan2 = DietPlan(
            plan_id="plan-002",
            patient_id="patient-001",
            generated_at=datetime(2024, 1, 2, 10, 0, 0),
            daily_calories=2000.0,
            macronutrient_targets=macros,
            meals=[meal],
            restrictions=[],
            recommendations=[],
            health_conditions=[]
        )
        data_store.save_diet_plan("patient-001", plan2)
        
        # Get history
        history = data_store.get_patient_history("patient-001")
        
        # Verify ordering (most recent first)
        assert len(history['plans']) == 2
        assert history['plans'][0]['id'] == "plan-002"  # Most recent
        assert history['plans'][1]['id'] == "plan-001"  # Older
    
    def test_delete_patient_data(self, data_store, sample_patient, sample_diet_plan):
        """Test deleting all patient data with verification."""
        # Save patient and diet plan
        data_store.save_patient(sample_patient, name="Jane Doe")
        data_store.save_diet_plan("patient-001", sample_diet_plan)
        
        # Delete patient data
        result = data_store.delete_patient_data("patient-001", user_id="user-123")
        
        assert result['success'] is True
        assert result['deleted_records']['patients'] == 1
        assert result['deleted_records']['diet_plans'] == 1
        assert result['verification']['complete'] is True
        assert result['verification']['total_remaining'] == 0
        
        # Verify data was deleted
        retrieved = data_store.get_patient("patient-001")
        assert retrieved is None
        
        history = data_store.get_patient_history("patient-001")
        assert len(history['plans']) == 0
    
    def test_delete_patient_data_without_verification(self, data_store, sample_patient):
        """Test deleting patient data without verification."""
        # Save patient
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Delete without verification
        result = data_store.delete_patient_data("patient-001", verify=False)
        
        assert result['success'] is True
        assert result['verification'] is None
        assert result['deleted_records']['patients'] == 1
    
    def test_delete_nonexistent_patient(self, data_store):
        """Test deleting a patient that doesn't exist."""
        result = data_store.delete_patient_data("nonexistent-id")
        
        assert result['success'] is True
        assert result['deleted_records']['patients'] == 0
        assert result['verification']['complete'] is True
    
    def test_check_duplicate_patient(self, data_store, sample_patient):
        """Test checking for duplicate patients."""
        # Initially no duplicate
        assert data_store.check_duplicate_patient("patient-001") is False
        
        # Save patient
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Now duplicate exists
        assert data_store.check_duplicate_patient("patient-001") is True
    
    def test_save_patient_duplicate_prevention(self, data_store, sample_patient):
        """Test that saving duplicate patient raises error."""
        # Save patient first time
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Try to save again - should raise ValueError
        with pytest.raises(ValueError, match="already exists"):
            data_store.save_patient(sample_patient, name="Jane Doe")
    
    def test_save_patient_allow_duplicate(self, data_store, sample_patient):
        """Test that allow_duplicate parameter bypasses duplicate check."""
        # Save patient first time
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Save again with allow_duplicate=True - should succeed
        patient_id = data_store.save_patient(
            sample_patient, 
            name="Jane Doe",
            allow_duplicate=True
        )
        assert patient_id == "patient-001"
    
    def test_get_or_create_patient_new(self, data_store, sample_patient):
        """Test get_or_create_patient with new patient."""
        patient_id, created = data_store.get_or_create_patient(
            sample_patient,
            name="Jane Doe",
            dob="1988-05-15"
        )
        
        assert patient_id == "patient-001"
        assert created is True
    
    def test_get_or_create_patient_existing(self, data_store, sample_patient):
        """Test get_or_create_patient with existing patient."""
        # Save patient first
        data_store.save_patient(sample_patient, name="Jane Doe")
        
        # Try to get_or_create - should return existing
        patient_id, created = data_store.get_or_create_patient(
            sample_patient,
            name="Jane Doe",
            dob="1988-05-15"
        )
        
        assert patient_id == "patient-001"
        assert created is False
    
    def test_audit_logging_on_operations(self, data_store, sample_patient):
        """Test that operations are logged in audit log."""
        # Perform operations
        data_store.save_patient(sample_patient, user_id="user-123", name="Jane Doe")
        data_store.get_patient("patient-001", user_id="user-123")
        data_store.delete_patient_data("patient-001", user_id="user-123")
        
        # Check audit log
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("SELECT action, resource_type FROM audit_log ORDER BY id")
            entries = cursor.fetchall()
            
            assert len(entries) >= 3
            assert entries[0][0] == "CREATE"  # save_patient
            assert entries[1][0] == "READ"    # get_patient
            assert entries[2][0] == "DELETE"  # delete_patient_data
    
    def test_encrypted_data_not_readable(self, data_store, sample_patient):
        """Test that sensitive data is encrypted in database."""
        # Save patient with sensitive data
        data_store.save_patient(
            sample_patient,
            name="Jane Doe",
            dob="1988-05-15"
        )
        
        # Read raw database
        import sqlite3
        with sqlite3.connect(data_store.db_path) as conn:
            cursor = conn.execute("SELECT encrypted_name, encrypted_dob FROM patients WHERE id = ?", ("patient-001",))
            row = cursor.fetchone()
            
            encrypted_name = row[0]
            encrypted_dob = row[1]
            
            # Encrypted data should not contain plaintext
            assert "Jane" not in encrypted_name
            assert "Doe" not in encrypted_name
            assert "1988" not in encrypted_dob
            
            # Should be base64-encoded
            import base64
            try:
                base64.b64decode(encrypted_name)
                base64.b64decode(encrypted_dob)
            except Exception:
                pytest.fail("Encrypted data is not valid base64")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
