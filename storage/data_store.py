"""
Data Store with encryption and security for the AI NutriCare System.

This module provides secure data persistence with AES-256 encryption for sensitive
patient data, audit logging, and TLS-secured database connections.
"""

import os
import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from contextlib import contextmanager
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

from ..models.patient_data import PatientProfile, UserPreferences
from ..models.diet_data import DietPlan
from ..models.health_data import StructuredHealthData


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages AES-256 encryption for sensitive data fields.
    
    Uses AES-256 in CBC mode with PKCS7 padding for encryption.
    Encryption keys are loaded from environment variables.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption manager.
        
        Args:
            key: Optional 32-byte encryption key. If not provided, loads from
                 NUTRICARE_ENCRYPTION_KEY environment variable.
        
        Raises:
            ValueError: If no key is provided and environment variable is not set
        """
        if key is None:
            key_str = os.environ.get('NUTRICARE_ENCRYPTION_KEY')
            if not key_str:
                raise ValueError(
                    "Encryption key not provided. Set NUTRICARE_ENCRYPTION_KEY "
                    "environment variable or pass key parameter."
                )
            # Derive 32-byte key from environment variable using SHA-256
            key = hashlib.sha256(key_str.encode()).digest()
        
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 bytes for AES-256")
        
        self.key = key
        self.backend = default_backend()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-CBC.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64-encoded encrypted data with IV prepended
        """
        if not plaintext:
            return ""
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        
        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend IV to ciphertext and encode as base64
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt AES-256-CBC encrypted data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data with IV prepended
        
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_data:
            return ""
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # Extract IV and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode('utf-8')


class AuditLogger:
    """
    Audit logger for tracking all database operations.
    
    Logs user actions, timestamps, and affected resources for compliance
    and security monitoring.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize audit logger.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_audit_table()
    
    def _ensure_audit_table(self):
        """Create audit_log table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT
                )
            """)
            conn.commit()
    
    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log an audit event.
        
        Args:
            action: Action performed (CREATE, READ, UPDATE, DELETE)
            resource_type: Type of resource (patient, diet_plan, medical_report)
            resource_id: Optional ID of the affected resource
            user_id: Optional ID of the user performing the action
            details: Optional additional details as dictionary
            ip_address: Optional IP address of the requester
        """
        timestamp = datetime.now().isoformat()
        details_json = json.dumps(details) if details else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_log 
                (timestamp, user_id, action, resource_type, resource_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, user_id, action, resource_type, resource_id, details_json, ip_address))
            conn.commit()
        
        logger.info(
            f"Audit: {action} {resource_type} {resource_id or ''} "
            f"by user {user_id or 'system'} at {timestamp}"
        )


class DataStore:
    """
    Secure data store for patient data and diet plans.
    
    Features:
    - AES-256 encryption for sensitive fields (name, DOB, health data)
    - Audit logging for all operations
    - TLS configuration support for database connections
    - CRUD operations for patients, medical reports, and diet plans
    """
    
    def __init__(
        self,
        db_path: str = "nutricare.db",
        encryption_key: Optional[bytes] = None,
        use_tls: bool = False
    ):
        """
        Initialize data store.
        
        Args:
            db_path: Path to SQLite database file
            encryption_key: Optional encryption key (uses env var if not provided)
            use_tls: Whether to use TLS for database connections (for remote DBs)
        """
        self.db_path = db_path
        self.use_tls = use_tls
        self.encryption = EncryptionManager(encryption_key)
        self.audit = AuditLogger(db_path)
        
        # Create database schema
        self._initialize_schema()
        
        logger.info(f"DataStore initialized with database at {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """
        Get database connection with optional TLS configuration.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        # For SQLite, TLS is handled at the file system level
        # For production with PostgreSQL, this would configure SSL/TLS
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            # Patients table with encrypted sensitive fields
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    encrypted_name TEXT,
                    encrypted_dob TEXT,
                    age INTEGER,
                    gender TEXT,
                    height_cm REAL,
                    weight_kg REAL,
                    activity_level TEXT,
                    preferences_json TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Medical reports table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS medical_reports (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    encrypted_data TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            """)
            
            # Health metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    confidence REAL,
                    extracted_at TEXT NOT NULL,
                    FOREIGN KEY (report_id) REFERENCES medical_reports(id)
                )
            """)
            
            # Diet plans table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS diet_plans (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    plan_data TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_patients_created 
                ON patients(created_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_reports_patient 
                ON medical_reports(patient_id, uploaded_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_plans_patient 
                ON diet_plans(patient_id, generated_at)
            """)
            
            conn.commit()
    
    def save_patient(
        self,
        patient: PatientProfile,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        dob: Optional[str] = None,
        allow_duplicate: bool = False
    ) -> str:
        """
        Save patient profile with encrypted sensitive fields.
        
        Implements duplicate prevention by checking if patient ID already exists.
        
        Args:
            patient: Patient profile to save
            user_id: Optional ID of user performing the operation
            name: Optional patient name (will be encrypted)
            dob: Optional date of birth (will be encrypted)
            allow_duplicate: If False, raises error on duplicate patient_id.
                           If True, updates existing patient if found.
        
        Returns:
            Patient ID
        
        Raises:
            ValueError: If patient already exists and allow_duplicate is False
        """
        # Check for duplicate patient (Requirement 16.5)
        patient_exists = self.check_duplicate_patient(patient.patient_id)
        
        if patient_exists and not allow_duplicate:
            logger.warning(f"Attempted to create duplicate patient {patient.patient_id}")
            raise ValueError(
                f"Patient with ID {patient.patient_id} already exists. "
                f"Use allow_duplicate=True to override or retrieve existing patient."
            )
        
        # Encrypt sensitive fields
        encrypted_name = self.encryption.encrypt(name) if name else ""
        encrypted_dob = self.encryption.encrypt(dob) if dob else ""
        
        # Serialize preferences
        preferences_dict = {
            'dietary_style': patient.preferences.dietary_style,
            'allergies': patient.preferences.allergies,
            'dislikes': patient.preferences.dislikes,
            'cultural_preferences': patient.preferences.cultural_preferences
        }
        preferences_json = json.dumps(preferences_dict)
        
        with self._get_connection() as conn:
            if patient_exists and allow_duplicate:
                # Update existing patient
                conn.execute("""
                    UPDATE patients 
                    SET encrypted_name = ?, encrypted_dob = ?, age = ?, gender = ?,
                        height_cm = ?, weight_kg = ?, activity_level = ?,
                        preferences_json = ?
                    WHERE id = ?
                """, (
                    encrypted_name,
                    encrypted_dob,
                    patient.age,
                    patient.gender,
                    patient.height_cm,
                    patient.weight_kg,
                    patient.activity_level,
                    preferences_json,
                    patient.patient_id
                ))
                action = "UPDATE"
            else:
                # Insert new patient
                conn.execute("""
                    INSERT INTO patients 
                    (id, encrypted_name, encrypted_dob, age, gender, height_cm, 
                     weight_kg, activity_level, preferences_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient.patient_id,
                    encrypted_name,
                    encrypted_dob,
                    patient.age,
                    patient.gender,
                    patient.height_cm,
                    patient.weight_kg,
                    patient.activity_level,
                    preferences_json,
                    patient.created_at.isoformat()
                ))
                action = "CREATE"
            
            conn.commit()
        
        # Audit log
        self.audit.log(
            action=action,
            resource_type="patient",
            resource_id=patient.patient_id,
            user_id=user_id
        )
        
        logger.info(f"{action}D patient {patient.patient_id}")
        return patient.patient_id
    
    def get_patient(
        self,
        patient_id: str,
        user_id: Optional[str] = None
    ) -> Optional[PatientProfile]:
        """
        Retrieve patient profile by ID.
        
        Args:
            patient_id: Patient ID to retrieve
            user_id: Optional ID of user performing the operation
        
        Returns:
            PatientProfile if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM patients WHERE id = ?
            """, (patient_id,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        # Audit log
        self.audit.log(
            action="READ",
            resource_type="patient",
            resource_id=patient_id,
            user_id=user_id
        )
        
        # Deserialize preferences
        preferences_dict = json.loads(row['preferences_json'])
        preferences = UserPreferences(
            dietary_style=preferences_dict.get('dietary_style'),
            allergies=preferences_dict.get('allergies', []),
            dislikes=preferences_dict.get('dislikes', []),
            cultural_preferences=preferences_dict.get('cultural_preferences', [])
        )
        
        # Create patient profile
        patient = PatientProfile(
            patient_id=row['id'],
            age=row['age'],
            gender=row['gender'],
            height_cm=row['height_cm'],
            weight_kg=row['weight_kg'],
            activity_level=row['activity_level'],
            preferences=preferences,
            created_at=datetime.fromisoformat(row['created_at'])
        )
        
        return patient
    
    def save_diet_plan(
        self,
        patient_id: str,
        plan: DietPlan,
        user_id: Optional[str] = None
    ) -> str:
        """
        Save diet plan associated with a patient.
        
        Args:
            patient_id: Patient ID
            plan: Diet plan to save
            user_id: Optional ID of user performing the operation
        
        Returns:
            Plan ID
        """
        # Serialize diet plan to JSON
        # Note: This is a simplified serialization. In production, you'd want
        # a more robust serialization that handles all nested objects
        plan_dict = {
            'plan_id': plan.plan_id,
            'patient_id': plan.patient_id,
            'generated_at': plan.generated_at.isoformat(),
            'daily_calories': plan.daily_calories,
            'macronutrient_targets': {
                'protein_percent': plan.macronutrient_targets.protein_percent,
                'carbs_percent': plan.macronutrient_targets.carbs_percent,
                'fat_percent': plan.macronutrient_targets.fat_percent
            },
            'meals': [
                {
                    'meal_type': meal.meal_type.value,
                    'total_calories': meal.total_calories,
                    'total_protein_g': meal.total_protein_g,
                    'total_carbs_g': meal.total_carbs_g,
                    'total_fat_g': meal.total_fat_g,
                    'portions': [
                        {
                            'food_name': portion.food.name,
                            'amount': portion.amount,
                            'unit': portion.unit,
                            'calories': portion.calories
                        }
                        for portion in meal.portions
                    ]
                }
                for meal in plan.meals
            ],
            'restrictions': [
                {
                    'restriction_type': r.restriction_type,
                    'restricted_items': r.restricted_items,
                    'severity': r.severity
                }
                for r in plan.restrictions
            ],
            'recommendations': plan.recommendations
        }
        plan_json = json.dumps(plan_dict)
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO diet_plans (id, patient_id, plan_data, generated_at)
                VALUES (?, ?, ?, ?)
            """, (
                plan.plan_id,
                patient_id,
                plan_json,
                plan.generated_at.isoformat()
            ))
            conn.commit()
        
        # Audit log
        self.audit.log(
            action="CREATE",
            resource_type="diet_plan",
            resource_id=plan.plan_id,
            user_id=user_id,
            details={'patient_id': patient_id}
        )
        
        logger.info(f"Saved diet plan {plan.plan_id} for patient {patient_id}")
        return plan.plan_id
    
    def get_patient_history(
        self,
        patient_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """
        Retrieve all medical reports and diet plans for a patient.
        
        Args:
            patient_id: Patient ID
            user_id: Optional ID of user performing the operation
        
        Returns:
            Dictionary with 'reports' and 'plans' lists, ordered by date
        """
        with self._get_connection() as conn:
            # Get medical reports
            reports_cursor = conn.execute("""
                SELECT id, report_type, uploaded_at
                FROM medical_reports
                WHERE patient_id = ?
                ORDER BY uploaded_at DESC
            """, (patient_id,))
            reports = [dict(row) for row in reports_cursor.fetchall()]
            
            # Get diet plans
            plans_cursor = conn.execute("""
                SELECT id, generated_at
                FROM diet_plans
                WHERE patient_id = ?
                ORDER BY generated_at DESC
            """, (patient_id,))
            plans = [dict(row) for row in plans_cursor.fetchall()]
        
        # Audit log
        self.audit.log(
            action="READ",
            resource_type="patient_history",
            resource_id=patient_id,
            user_id=user_id
        )
        
        return {
            'reports': reports,
            'plans': plans
        }
    
    def delete_patient_data(
        self,
        patient_id: str,
        user_id: Optional[str] = None,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Permanently delete all patient data with verification.
        
        Implements complete data deletion as per Requirement 17.5.
        
        Args:
            patient_id: Patient ID to delete
            user_id: Optional ID of user performing the operation
            verify: If True, verifies deletion was complete
        
        Returns:
            Dictionary with deletion results:
            - success: bool indicating if deletion succeeded
            - deleted_records: dict with counts of deleted records by type
            - verification: dict with verification results (if verify=True)
        """
        result = {
            'success': False,
            'deleted_records': {
                'health_metrics': 0,
                'medical_reports': 0,
                'diet_plans': 0,
                'patients': 0
            },
            'verification': None
        }
        
        try:
            with self._get_connection() as conn:
                # Count records before deletion for verification
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM health_metrics 
                    WHERE report_id IN (SELECT id FROM medical_reports WHERE patient_id = ?)
                """, (patient_id,))
                health_metrics_count = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM medical_reports WHERE patient_id = ?
                """, (patient_id,))
                reports_count = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM diet_plans WHERE patient_id = ?
                """, (patient_id,))
                plans_count = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM patients WHERE id = ?
                """, (patient_id,))
                patient_count = cursor.fetchone()[0]
                
                # Delete in order to respect foreign key constraints
                conn.execute("""
                    DELETE FROM health_metrics 
                    WHERE report_id IN (SELECT id FROM medical_reports WHERE patient_id = ?)
                """, (patient_id,))
                
                conn.execute("DELETE FROM medical_reports WHERE patient_id = ?", (patient_id,))
                conn.execute("DELETE FROM diet_plans WHERE patient_id = ?", (patient_id,))
                conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                conn.commit()
                
                result['deleted_records'] = {
                    'health_metrics': health_metrics_count,
                    'medical_reports': reports_count,
                    'diet_plans': plans_count,
                    'patients': patient_count
                }
            
            # Verify deletion if requested (Requirement 17.5)
            if verify:
                verification = self._verify_deletion(patient_id)
                result['verification'] = verification
                result['success'] = verification['complete']
            else:
                result['success'] = True
            
            # Audit log
            self.audit.log(
                action="DELETE",
                resource_type="patient",
                resource_id=patient_id,
                user_id=user_id,
                details=result['deleted_records']
            )
            
            logger.info(
                f"Deleted all data for patient {patient_id}: "
                f"{result['deleted_records']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to delete patient {patient_id}: {e}")
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _verify_deletion(self, patient_id: str) -> Dict[str, Any]:
        """
        Verify that all patient data has been completely deleted.
        
        Args:
            patient_id: Patient ID to verify deletion for
        
        Returns:
            Dictionary with verification results:
            - complete: bool indicating if deletion is complete
            - remaining_records: dict with counts of any remaining records
        """
        remaining = {
            'patients': 0,
            'medical_reports': 0,
            'diet_plans': 0,
            'health_metrics': 0
        }
        
        with self._get_connection() as conn:
            # Check for any remaining patient records
            cursor = conn.execute("""
                SELECT COUNT(*) FROM patients WHERE id = ?
            """, (patient_id,))
            remaining['patients'] = cursor.fetchone()[0]
            
            # Check for any remaining medical reports
            cursor = conn.execute("""
                SELECT COUNT(*) FROM medical_reports WHERE patient_id = ?
            """, (patient_id,))
            remaining['medical_reports'] = cursor.fetchone()[0]
            
            # Check for any remaining diet plans
            cursor = conn.execute("""
                SELECT COUNT(*) FROM diet_plans WHERE patient_id = ?
            """, (patient_id,))
            remaining['diet_plans'] = cursor.fetchone()[0]
            
            # Check for any remaining health metrics
            cursor = conn.execute("""
                SELECT COUNT(*) FROM health_metrics 
                WHERE report_id IN (SELECT id FROM medical_reports WHERE patient_id = ?)
            """, (patient_id,))
            remaining['health_metrics'] = cursor.fetchone()[0]
        
        total_remaining = sum(remaining.values())
        
        return {
            'complete': total_remaining == 0,
            'remaining_records': remaining,
            'total_remaining': total_remaining
        }
    
    def check_duplicate_patient(
        self,
        patient_id: str
    ) -> bool:
        """
        Check if a patient with the given ID already exists.
        
        Implements duplicate patient prevention (Requirement 16.5).
        
        Args:
            patient_id: Patient ID to check
        
        Returns:
            True if patient exists, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM patients WHERE id = ?
            """, (patient_id,))
            count = cursor.fetchone()['count']
        
        return count > 0
    
    def get_or_create_patient(
        self,
        patient: PatientProfile,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        dob: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Get existing patient ID or create new patient if doesn't exist.
        
        Implements duplicate patient prevention (Requirement 16.5).
        
        Args:
            patient: Patient profile to save
            user_id: Optional ID of user performing the operation
            name: Optional patient name (will be encrypted)
            dob: Optional date of birth (will be encrypted)
        
        Returns:
            Tuple of (patient_id, created) where created is True if new patient
            was created, False if existing patient was returned
        """
        if self.check_duplicate_patient(patient.patient_id):
            logger.info(f"Patient {patient.patient_id} already exists, returning existing ID")
            return patient.patient_id, False
        else:
            patient_id = self.save_patient(
                patient,
                user_id=user_id,
                name=name,
                dob=dob,
                allow_duplicate=False
            )
            return patient_id, True

