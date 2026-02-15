# Data Storage with Encryption and Security

This module provides secure data persistence for the AI NutriCare System with comprehensive security features.

## Features

### 1. AES-256 Encryption
- **Algorithm**: AES-256 in CBC mode with PKCS7 padding
- **Key Management**: 32-byte keys loaded from environment variables
- **Encrypted Fields**: Patient names, dates of birth, and other sensitive health information
- **Random IV**: Each encryption uses a unique initialization vector for security

### 2. Audit Logging
- **Comprehensive Tracking**: All database operations (CREATE, READ, UPDATE, DELETE) are logged
- **Audit Information**: Timestamp, user ID, action, resource type, resource ID, details, IP address
- **Compliance**: Supports HIPAA audit requirements for healthcare data

### 3. TLS Configuration
- **Secure Connections**: Support for TLS 1.2+ for database connections
- **Production Ready**: Designed to work with PostgreSQL SSL/TLS in production
- **Development Mode**: Uses SQLite with file-system level security for development

### 4. Data Persistence
- **Patient Profiles**: Store patient demographics and preferences
- **Medical Reports**: Store uploaded medical reports with encryption
- **Health Metrics**: Store extracted health metrics from reports
- **Diet Plans**: Store generated personalized diet plans
- **Indexes**: Optimized queries with B-tree indexes on frequently accessed fields

### 5. Query Operations
- **Patient History Retrieval**: Get all medical reports and diet plans ordered by date (most recent first)
- **Duplicate Prevention**: Automatic detection and prevention of duplicate patient records
- **Get or Create**: Idempotent patient creation that returns existing patient if found

### 6. Deletion Operations
- **Complete Data Deletion**: Permanently remove all patient data (GDPR/HIPAA compliance)
- **Verification**: Automatic verification that all records were successfully deleted
- **Cascade Deletion**: Automatically removes all related records (reports, plans, metrics)

## Setup

### Environment Variables

Set the encryption key as an environment variable:

```bash
# Linux/Mac
export NUTRICARE_ENCRYPTION_KEY="your-secure-encryption-key-here"

# Windows
set NUTRICARE_ENCRYPTION_KEY=your-secure-encryption-key-here
```

**Important**: In production, use a secure key management system like:
- AWS KMS (Key Management Service)
- HashiCorp Vault
- Azure Key Vault
- Google Cloud KMS

### Installation

Install required dependencies:

```bash
pip install cryptography>=41.0.0
```

## Usage

### Basic Usage

```python
from ai_diet_planner.storage import DataStore
from ai_diet_planner.models.patient_data import PatientProfile, UserPreferences
from datetime import datetime

# Initialize data store
data_store = DataStore(db_path="nutricare.db")

# Create patient profile
preferences = UserPreferences(
    dietary_style="vegetarian",
    allergies=["peanuts"],
    dislikes=["mushrooms"]
)

patient = PatientProfile(
    patient_id="patient-001",
    age=35,
    gender="female",
    height_cm=165.0,
    weight_kg=68.0,
    activity_level="moderate",
    preferences=preferences,
    created_at=datetime.now()
)

# Save patient with encrypted sensitive data
data_store.save_patient(
    patient,
    user_id="doctor-123",
    name="Jane Doe",  # Will be encrypted
    dob="1988-05-15"  # Will be encrypted
)

# Retrieve patient
retrieved_patient = data_store.get_patient(
    "patient-001",
    user_id="doctor-123"
)

# Get patient history (ordered by date, most recent first)
history = data_store.get_patient_history(
    "patient-001",
    user_id="doctor-123"
)
print(f"Medical reports: {len(history['reports'])}")
print(f"Diet plans: {len(history['plans'])}")

# Check for duplicate patients
is_duplicate = data_store.check_duplicate_patient("patient-001")
print(f"Patient exists: {is_duplicate}")

# Get or create patient (idempotent operation)
patient_id, created = data_store.get_or_create_patient(
    patient,
    user_id="doctor-123",
    name="Jane Doe",
    dob="1988-05-15"
)
print(f"Patient ID: {patient_id}, Created: {created}")

# Delete patient data with verification (GDPR compliance)
result = data_store.delete_patient_data(
    "patient-001",
    user_id="doctor-123",
    verify=True  # Verify deletion was complete
)
print(f"Deletion successful: {result['success']}")
print(f"Records deleted: {result['deleted_records']}")
print(f"Verification complete: {result['verification']['complete']}")
```

### Duplicate Prevention

```python
# Try to save duplicate patient (will raise ValueError)
try:
    data_store.save_patient(patient, name="Jane Doe")
except ValueError as e:
    print(f"Duplicate prevented: {e}")

# Allow duplicate (updates existing patient)
data_store.save_patient(
    patient,
    name="Jane Doe",
    allow_duplicate=True  # Updates existing patient
)

# Use get_or_create for idempotent operations
patient_id, created = data_store.get_or_create_patient(
    patient,
    name="Jane Doe"
)
if created:
    print("New patient created")
else:
    print("Existing patient returned")
```

### Custom Encryption Key

```python
# Provide encryption key directly (for testing)
encryption_key = b'0' * 32  # 32-byte key
data_store = DataStore(
    db_path="test.db",
    encryption_key=encryption_key
)
```

### TLS Configuration

```python
# Enable TLS for production database connections
data_store = DataStore(
    db_path="nutricare.db",
    use_tls=True
)
```

## Security Best Practices

### 1. Key Management
- **Never hardcode encryption keys** in source code
- Use environment variables for development
- Use dedicated key management services for production
- Rotate encryption keys periodically
- Store keys separately from encrypted data

### 2. Access Control
- Always provide `user_id` parameter for audit logging
- Implement authentication before database operations
- Use role-based access control (RBAC)
- Log all access attempts

### 3. Data Protection
- Encrypt sensitive fields (names, DOB, health data)
- Use TLS for all network communications
- Implement secure backup procedures
- Follow HIPAA compliance guidelines

### 4. Audit Compliance
- Review audit logs regularly
- Set up alerts for suspicious activities
- Retain audit logs per compliance requirements
- Implement log rotation and archival

## Database Schema

### Patients Table
```sql
CREATE TABLE patients (
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
```

### Medical Reports Table
```sql
CREATE TABLE medical_reports (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    encrypted_data TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
)
```

### Health Metrics Table
```sql
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    confidence REAL,
    extracted_at TEXT NOT NULL,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id)
)
```

### Diet Plans Table
```sql
CREATE TABLE diet_plans (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    plan_data TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
)
```

### Audit Log Table
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details TEXT,
    ip_address TEXT
)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest ai_diet_planner/storage/test_data_store.py -v

# Run specific test class
pytest ai_diet_planner/storage/test_data_store.py::TestEncryptionManager -v

# Run with coverage
pytest ai_diet_planner/storage/test_data_store.py --cov=ai_diet_planner.storage
```

## Compliance

This implementation supports:
- **HIPAA**: Encryption at rest, audit logging, access controls
- **GDPR**: Right to deletion, data portability, audit trails
- **HITECH**: Breach notification support through audit logs

## Performance

- **Indexes**: B-tree indexes on `patient_id` and `created_at` for fast queries
  - `idx_patients_created`: Index on `patients(created_at)` for chronological queries
  - `idx_reports_patient`: Composite index on `medical_reports(patient_id, uploaded_at)` for patient history
  - `idx_plans_patient`: Composite index on `diet_plans(patient_id, generated_at)` for diet plan retrieval
- **Connection Pooling**: Context managers for efficient connection handling
- **Batch Operations**: Support for bulk inserts and updates
- **Query Optimization**: Optimized queries with proper indexing for O(log n) lookups

## Migration to Production

For production deployment:

1. **Switch to PostgreSQL**:
   ```python
   # Use PostgreSQL with SSL/TLS
   import psycopg2
   # Configure connection with SSL parameters
   ```

2. **Use Key Management Service**:
   ```python
   # Example with AWS KMS
   import boto3
   kms = boto3.client('kms')
   # Retrieve encryption key from KMS
   ```

3. **Enable Connection Pooling**:
   ```python
   # Use connection pooling for better performance
   from psycopg2 import pool
   connection_pool = pool.SimpleConnectionPool(1, 20, ...)
   ```

4. **Set up Monitoring**:
   - Monitor audit logs for suspicious activity
   - Set up alerts for failed authentication attempts
   - Track database performance metrics

## Troubleshooting

### Encryption Key Not Found
```
ValueError: Encryption key not provided. Set NUTRICARE_ENCRYPTION_KEY environment variable
```
**Solution**: Set the `NUTRICARE_ENCRYPTION_KEY` environment variable or pass the key directly.

### Database Locked
```
sqlite3.OperationalError: database is locked
```
**Solution**: SQLite doesn't handle concurrent writes well. For production, use PostgreSQL.

### Decryption Failed
```
cryptography.exceptions.InvalidTag: ...
```
**Solution**: Ensure you're using the same encryption key that was used to encrypt the data.

## License

This module is part of the AI NutriCare System and follows the same license.
