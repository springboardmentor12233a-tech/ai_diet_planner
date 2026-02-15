-- AI NutriCare System - Initial Database Schema
-- Migration: 001_initial_schema
-- Date: 2026-02-15

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT UNIQUE NOT NULL,
    name_encrypted BLOB NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    height_cm REAL NOT NULL,
    weight_kg REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_created_at ON patients(created_at);

-- Medical reports table
CREATE TABLE IF NOT EXISTS medical_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_path TEXT NOT NULL,
    report_content_encrypted BLOB,
    ocr_confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_report_patient_id ON medical_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_report_created_at ON medical_reports(created_at);

-- Health metrics table
CREATE TABLE IF NOT EXISTS health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_id INTEGER NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    is_abnormal BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metric_patient_id ON health_metrics(patient_id);
CREATE INDEX IF NOT EXISTS idx_metric_type ON health_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metric_created_at ON health_metrics(created_at);

-- Health conditions table
CREATE TABLE IF NOT EXISTS health_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_id INTEGER NOT NULL,
    condition_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_condition_patient_id ON health_conditions(patient_id);
CREATE INDEX IF NOT EXISTS idx_condition_type ON health_conditions(condition_type);

-- Health alerts table
CREATE TABLE IF NOT EXISTS health_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alert_patient_id ON health_alerts(patient_id);
CREATE INDEX IF NOT EXISTS idx_alert_severity ON health_alerts(severity);

-- Diet rules table
CREATE TABLE IF NOT EXISTS diet_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_id INTEGER NOT NULL,
    rule_text TEXT NOT NULL,
    priority TEXT NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rule_patient_id ON diet_rules(patient_id);
CREATE INDEX IF NOT EXISTS idx_rule_priority ON diet_rules(priority);

-- Diet plans table
CREATE TABLE IF NOT EXISTS diet_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    report_id INTEGER NOT NULL,
    plan_data_encrypted BLOB NOT NULL,
    daily_calories REAL NOT NULL,
    pdf_path TEXT,
    json_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES medical_reports(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_plan_patient_id ON diet_plans(patient_id);
CREATE INDEX IF NOT EXISTS idx_plan_created_at ON diet_plans(created_at);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_patient_id ON audit_log(patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    dietary_preference TEXT,
    cuisine_preferences TEXT,
    disliked_foods TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pref_patient_id ON user_preferences(patient_id);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES (1, 'Initial schema');
