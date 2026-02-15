# Implementation Plan: AI NutriCare System

## Overview

This implementation plan breaks down the AI NutriCare System into discrete, incremental coding tasks. The system will be built in phases, starting with core data models and utilities, then building up through OCR, data extraction, ML analysis, NLP interpretation, diet plan generation, export functionality, data persistence, and finally the user interface. Each task builds on previous work, with testing integrated throughout to catch errors early.

The implementation leverages the existing codebase in `ai_diet_planner/` and extends it with new components following the design architecture.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create `ai_diet_planner/models/` directory for data models
  - Implement core data classes: HealthMetric, StructuredHealthData, TextualNote, Alert, HealthCondition, DietRule, DietaryRestriction, Food, Portion, Meal, DietPlan, PatientProfile, UserPreferences
  - Implement enums: MetricType, AlertSeverity, ConditionType, RulePriority, MealType
  - Add type hints and docstrings for all data models
  - _Requirements: 3.1, 3.2, 5.4, 8.1, 9.1, 16.1_

- [ ]* 1.1 Write property tests for data model serialization
  - **Property: Data model round-trip serialization**
  - **Validates: Requirements 3.4, 12.3**
  - Test that all data models can be serialized to JSON and deserialized back to equivalent objects

- [ ] 2. Implement Medical Report Processor
  - [x] 2.1 Create `ai_diet_planner/processor/report_processor.py`
    - Implement MedicalReportProcessor class with file validation
    - Add support for PDF, JPEG, PNG, TIFF, TXT formats
    - Implement file size validation (max 10MB)
    - Add format detection using magic bytes and extensions
    - Implement processing queue using simple in-memory queue (can upgrade to Celery later)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 2.2 Write property tests for file acceptance and rejection
    - **Property 1: Valid file format acceptance**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - **Property 2: File size rejection**
    - **Validates: Requirements 1.4**
    - **Property 3: Unsupported format rejection**
    - **Validates: Requirements 1.5**

- [ ] 3. Enhance OCR Engine
  - [x] 3.1 Refactor existing OCR code into unified OCREngine class
    - Move `ocr/ocr_images.py` and `ocr/ocr_pdf.py` into `ocr/ocr_engine.py`
    - Implement OCREngine class with configurable backend (Tesseract/EasyOCR)
    - Add image preprocessing pipeline (grayscale, noise reduction, contrast enhancement, binarization, deskewing)
    - Implement confidence scoring for OCR results
    - Add quality check with 60% minimum confidence threshold
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

  - [ ]* 3.2 Write property tests for OCR accuracy and error handling
    - **Property 4: OCR accuracy threshold**
    - **Validates: Requirements 2.1, 2.2**
    - **Property 5: OCR quality error handling**
    - **Validates: Requirements 2.3**
    - **Property 7: Page order preservation**
    - **Validates: Requirements 2.5**

- [ ] 4. Implement Data Extractor
  - [x] 4.1 Create `ai_diet_planner/extraction/data_extractor.py`
    - Implement DataExtractor class with regex patterns for health metrics
    - Add patterns for: glucose, cholesterol (total/LDL/HDL), triglycerides, BMI, blood pressure, hemoglobin, HbA1c
    - Implement unit normalization (convert all to standard units)
    - Add context analysis for metric type disambiguation
    - Implement section detection (Lab Results, Doctor Notes, Prescriptions)
    - Add ambiguity flagging for unclear values
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 4.2 Implement textual notes extraction
    - Add note section identification
    - Implement context preservation for related notes
    - Add encrypted/redacted text detection and exclusion
    - Separate structured metrics from textual notes in output
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 4.3 Write property tests for data extraction
    - **Property 8: Health metric extraction completeness**
    - **Validates: Requirements 3.1**
    - **Property 9: Metric type classification accuracy**
    - **Validates: Requirements 3.2**
    - **Property 11: Structured data JSON output**
    - **Validates: Requirements 3.4, 8.4, 12.3**
    - **Property 13: Textual notes extraction**
    - **Validates: Requirements 4.1**

  - [ ]* 4.4 Write unit tests for edge cases
    - Test empty input, malformed data, missing units
    - Test ambiguous values, multiple metrics in one line
    - Test encrypted/redacted content exclusion
    - _Requirements: 3.3, 3.5, 4.4_

- [x] 5. Checkpoint - Ensure data extraction pipeline works end-to-end
  - Test: Upload sample medical report → OCR → Extract metrics and notes
  - Verify extracted data matches expected format
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Enhance ML Health Analyzer
  - [x] 6.1 Refactor existing ML code into MLHealthAnalyzer class
    - Move `ml/diabetes_train*.py` logic into `ml/health_analyzer.py`
    - Implement MLHealthAnalyzer class with model registry
    - Add support for multiple models: XGBoost, LightGBM, Random Forest, Logistic Regression
    - Implement feature engineering: standardization, feature selection, interaction features
    - Add 5-fold stratified cross-validation
    - Implement class balancing using SMOTE
    - _Requirements: 5.1, 5.2, 18.1_

  - [x] 6.2 Implement health condition classification
    - Add classification for: diabetes (type 1/2, prediabetes), hypertension (stage 1/2), hyperlipidemia, obesity (class I/II/III), anemia
    - Implement confidence scoring for predictions
    - Add handling for incomplete metrics
    - Output HealthCondition objects with contributing metrics
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [x] 6.3 Enhance health alerts system
    - Refactor `ml/health_alerts.py` into MLHealthAnalyzer
    - Implement threshold-based alert generation
    - Add severity levels: CRITICAL, WARNING, NORMAL
    - Implement alert prioritization by medical severity
    - Add recommended actions to alerts
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.4 Implement model registry and versioning
    - Create model storage with version metadata
    - Add model loading with compatibility verification
    - Implement automatic retraining flag for accuracy < 85%
    - Add model evaluation metrics reporting (accuracy, precision, recall, F1)
    - _Requirements: 18.2, 18.3, 18.4, 18.5_

  - [ ]* 6.5 Write property tests for ML health analyzer
    - **Property 17: ML classification execution**
    - **Validates: Requirements 5.1**
    - **Property 18: Critical condition flagging**
    - **Validates: Requirements 5.3**
    - **Property 22: Abnormal value alert generation**
    - **Validates: Requirements 6.2, 6.4**
    - **Property 23: Alert prioritization by severity**
    - **Validates: Requirements 6.3**

  - [ ]* 6.6 Write unit tests for ML model training and validation
    - Test cross-validation execution
    - Test model evaluation metrics
    - Test retraining flag logic
    - Test model versioning and compatibility
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

- [ ] 7. Implement NLP Text Interpreter
  - [x] 7.1 Create `ai_diet_planner/nlp/text_interpreter.py`
    - Implement NLPTextInterpreter class with GPT-4 integration (OpenAI API)
    - Add prompt engineering for medical context
    - Implement few-shot learning with example medical notes
    - Set temperature=0.3 for consistent outputs
    - Add fallback to BERT-based NER model
    - _Requirements: 7.1, 7.2_

  - [x] 7.2 Implement diet rule extraction
    - Extract dietary restrictions (allergies, intolerances) with REQUIRED priority
    - Extract dietary recommendations with RECOMMENDED priority
    - Implement ambiguous instruction flagging
    - Add caching for common note patterns (24-hour TTL)
    - _Requirements: 7.3, 7.4, 7.5_

  - [x] 7.3 Refactor and enhance rules mapping
    - Enhance `nlp/rules_mapping.py` with food category mapping
    - Map diet rules to food categories (proteins, carbs, fats, dairy, etc.)
    - Implement priority assignment (REQUIRED, RECOMMENDED, OPTIONAL)
    - Add conflict resolution using medical priority hierarchies
    - Output structured DietRules in JSON format
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 7.4 Write property tests for NLP text interpreter
    - **Property 25: Dietary restriction extraction with priority**
    - **Validates: Requirements 7.3**
    - **Property 26: Dietary recommendation extraction**
    - **Validates: Requirements 7.4**
    - **Property 28: Diet rule to food category mapping**
    - **Validates: Requirements 8.1**
    - **Property 30: Diet rule conflict resolution**
    - **Validates: Requirements 8.3**

  - [ ]* 7.5 Write unit tests for NLP edge cases
    - Test ambiguous instructions flagging
    - Test contradictory rules handling
    - Test API timeout and fallback to BERT
    - Test caching behavior
    - _Requirements: 7.5, 8.3_

- [x] 8. Checkpoint - Ensure analysis pipeline works end-to-end
  - Test: Extracted metrics → ML classification → Health conditions and alerts
  - Test: Extracted notes → NLP interpretation → Diet rules
  - Verify outputs match expected formats
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement Diet Plan Generator
  - [x] 9.1 Create `ai_diet_planner/generation/diet_planner.py`
    - Implement DietPlanGenerator class
    - Integrate USDA FoodData Central API for food database
    - Implement daily caloric needs calculation (Mifflin-St Jeor equation)
    - Add macronutrient target calculation based on health conditions
    - _Requirements: 9.1, 9.3_

  - [x] 9.2 Implement meal generation with constraint satisfaction
    - Filter food database by dietary restrictions and allergies
    - Implement constraint satisfaction for food selection
    - Generate meals for breakfast (25%), lunch (35%), snack (10%), dinner (30%) of daily calories
    - Calculate portions to meet caloric and macronutrient targets
    - Ensure variety optimization across meals
    - _Requirements: 9.1, 9.2, 9.4, 10.1, 10.2_

  - [x] 9.3 Implement conflict resolution and priority handling
    - Prioritize medical restrictions over user preferences
    - Handle impossible constraint scenarios with alternative recommendations
    - Add user notification for preference conflicts
    - _Requirements: 9.5, 10.3, 10.4_

  - [ ]* 9.4 Write property tests for diet plan generator
    - **Property 31: Diet plan meal structure**
    - **Validates: Requirements 9.1**
    - **Property 32: Diet plan rule compliance**
    - **Validates: Requirements 9.2**
    - **Property 33: Macronutrient balance**
    - **Validates: Requirements 9.3**
    - **Property 37: Allergy exclusion (Safety Critical)**
    - **Validates: Requirements 10.2**
    - Run with 1000+ iterations for safety-critical Property 37

  - [ ]* 9.5 Write unit tests for diet plan generation
    - Test specific health condition scenarios (diabetes, hypertension, obesity)
    - Test dietary preference integration (vegetarian, vegan, keto)
    - Test conflict resolution between preferences and medical requirements
    - Test alternative recommendations for impossible constraints
    - _Requirements: 9.5, 10.1, 10.3, 10.4_

- [ ] 10. Implement Report Exporter
  - [x] 10.1 Create `ai_diet_planner/export/report_exporter.py`
    - Implement ReportExporter class
    - Add PDF generation using ReportLab
    - Create professional medical report template
    - Add sections: Patient Info, Health Summary, Diet Plan, Nutritional Breakdown
    - Include visual elements: macronutrient charts, meal tables
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 10.2 Implement JSON export
    - Add JSON export with schema validation
    - Include all diet plan data: meals, portions, nutrients, restrictions, recommendations
    - Validate against defined JSON schema
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 10.3 Add error handling and performance optimization
    - Implement descriptive error messages for generation failures
    - Optimize PDF generation to complete within 5 seconds
    - Optimize JSON generation to complete within 2 seconds
    - _Requirements: 11.4, 11.5, 12.4_

  - [ ]* 10.4 Write property tests for report exporter
    - **Property 39: PDF generation completeness**
    - **Validates: Requirements 11.1, 11.2**
    - **Property 40: PDF generation performance**
    - **Validates: Requirements 11.4**
    - **Property 42: JSON export completeness**
    - **Validates: Requirements 12.1, 12.2**
    - **Property 43: JSON generation performance**
    - **Validates: Requirements 12.4**

  - [ ]* 10.5 Write unit tests for export functionality
    - Test PDF generation with sample diet plans
    - Test JSON schema validation
    - Test error handling for generation failures
    - _Requirements: 11.5_

- [x] 11. Implement Data Store
  - [x] 11.1 Create `ai_diet_planner/storage/data_store.py`
    - Implement DataStore class with SQLite for development
    - Create database schema: patients, medical_reports, health_metrics, diet_plans, audit_log
    - Implement CRUD operations for all entities
    - Add unique patient identifier generation
    - _Requirements: 16.1, 16.2_

  - [x] 11.2 Implement encryption and security
    - Add AES-256 encryption for sensitive fields
    - Implement key management (environment variables for development)
    - Add TLS configuration for database connections
    - Implement authentication and audit logging
    - _Requirements: 16.3, 17.2, 17.3, 17.4_

  - [x] 11.3 Implement query and deletion operations
    - Add patient history retrieval ordered by date
    - Implement duplicate patient prevention
    - Add complete data deletion with verification
    - Create indexes for performance (patient_id, created_at)
    - _Requirements: 16.4, 16.5, 17.5_

  - [ ]* 11.4 Write property tests for data store
    - **Property 48: Patient data persistence with unique ID**
    - **Validates: Requirements 16.1**
    - **Property 50: Data encryption at rest**
    - **Validates: Requirements 16.3, 17.2**
    - **Property 52: Duplicate patient prevention**
    - **Validates: Requirements 16.5**
    - **Property 55: Complete data deletion**
    - **Validates: Requirements 17.5**

  - [ ]* 11.5 Write unit tests for data store operations
    - Test CRUD operations
    - Test encryption/decryption
    - Test audit logging
    - Test query performance with indexes
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 17.4_

- [ ] 12. Checkpoint - Ensure backend pipeline works end-to-end
  - Test: Upload report → Process → Analyze → Generate plan → Export → Store
  - Verify data persistence and retrieval
  - Verify encryption and security measures
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement error handling and recovery
  - [x] 13.1 Create `ai_diet_planner/utils/error_handler.py`
    - Implement centralized error logging with timestamp, context, stack trace
    - Add error categories: InputValidation, Processing, Data, System
    - Implement graceful degradation strategies
    - Add retry logic with exponential backoff for transient failures
    - _Requirements: 19.1, 19.2_

  - [x] 13.2 Implement fallback mechanisms
    - Add OCR failure → manual data entry fallback
    - Add ML failure → rule-based threshold analysis fallback
    - Add NLP failure → manual diet rule entry fallback
    - Add descriptive user-facing error messages
    - _Requirements: 19.3, 19.4, 19.5_

  - [ ]* 13.3 Write property tests for error handling
    - **Property 61: Error logging completeness**
    - **Validates: Requirements 19.1**
    - **Property 62: Pipeline failure recovery**
    - **Validates: Requirements 19.2**
    - **Property 63: OCR failure fallback**
    - **Validates: Requirements 19.3**

  - [ ]* 13.4 Write unit tests for error scenarios
    - Test all error categories
    - Test retry logic with transient failures
    - Test fallback mechanisms
    - Test error message clarity
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [x] 14. Implement User Interface with Streamlit
  - [x] 14.1 Create `ai_diet_planner/ui/app.py` main application
    - Set up Streamlit application structure
    - Implement multi-page navigation: Upload, Review, Diet Plan, History
    - Add session state management
    - _Requirements: 13.1, 13.5_

  - [x] 14.2 Implement Upload page
    - Add file upload component with drag-and-drop
    - Display supported formats and size limits
    - Show upload progress bar
    - Display confirmation/error messages
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [x] 14.3 Implement Review page (data summary)
    - Display extracted health metrics in table format
    - Highlight abnormal values with color coding
    - Show detected health conditions with confidence scores
    - Display alerts prioritized by severity
    - Add edit controls for correcting extracted values
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 14.4 Implement Diet Plan page
    - Display diet plan organized by meal times
    - Show food items, portions, and nutritional info for each meal
    - Highlight dietary restrictions and special considerations
    - Add Plotly charts for macronutrient balance visualization
    - Provide PDF and JSON export buttons
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 14.5 Implement History page
    - Display list of past medical reports and diet plans
    - Add filtering and sorting by date
    - Allow viewing and re-exporting previous plans
    - _Requirements: 16.4_

  - [ ]* 14.6 Write property tests for UI components
    - **Property 44: UI upload feedback**
    - **Validates: Requirements 13.2, 13.3, 13.4**
    - **Property 45: Health data visualization**
    - **Validates: Requirements 14.2, 14.4**
    - **Property 46: Diet plan UI organization**
    - **Validates: Requirements 15.1, 15.2**

  - [ ]* 14.7 Write unit tests for UI rendering
    - Test component rendering with sample data
    - Test error message display
    - Test export button functionality
    - Test navigation between pages
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 14.1, 14.5, 15.5_

- [x] 15. Integration and end-to-end wiring
  - [x] 15.1 Create main application orchestrator
    - Implement `ai_diet_planner/main.py` to wire all components
    - Connect Medical Report Processor → OCR Engine → Data Extractor
    - Connect Data Extractor → ML Health Analyzer + NLP Text Interpreter
    - Connect Analyzers → Diet Plan Generator → Report Exporter → Data Store
    - Connect backend to Streamlit UI
    - _Requirements: 2.4, all integration requirements_

  - [x] 15.2 Add configuration management
    - Create `ai_diet_planner/config.py` for centralized configuration
    - Add environment variables for API keys (OpenAI, USDA FoodData)
    - Add database connection settings
    - Add model paths and versions
    - Add performance thresholds and timeouts

  - [x] 15.3 Add logging and monitoring
    - Set up structured logging throughout application
    - Add performance monitoring for processing times
    - Add health check endpoints
    - Add metrics collection for error rates

  - [ ]* 15.4 Write integration tests
    - Test complete workflow: PDF upload → diet plan export
    - Test complete workflow: Image upload → diet plan export
    - Test complete workflow: Manual text entry → diet plan export
    - Test error recovery scenarios
    - Test concurrent user scenarios
    - _Requirements: All requirements_

- [ ] 16. Performance optimization and testing
  - [ ] 16.1 Implement caching layer
    - Add Redis cache for NLP results (24-hour TTL)
    - Add cache for ML model predictions
    - Add cache for USDA food database queries
    - _Requirements: 20.1, 20.2, 20.3_

  - [ ] 16.2 Optimize processing pipeline
    - Add parallel processing for multi-page OCR
    - Optimize database queries with proper indexing
    - Optimize PDF generation with template caching
    - _Requirements: 20.1, 20.2, 20.4, 20.5_

  - [ ]* 16.3 Write performance tests
    - **Property 66: Single-page processing performance**
    - **Validates: Requirements 20.1**
    - **Property 67: Multi-page processing performance**
    - **Validates: Requirements 20.2**
    - **Property 68: Concurrent processing scalability**
    - **Validates: Requirements 20.3**
    - **Property 69: Diet plan generation performance**
    - **Validates: Requirements 20.4**

- [ ] 17. Documentation and deployment preparation
  - [x] 17.1 Update project documentation
    - Update README.md with setup instructions
    - Add API documentation for all components
    - Create user guide for the Streamlit interface
    - Document configuration options

  - [x] 17.2 Create deployment scripts
    - Add requirements.txt with all dependencies
    - Create Docker configuration for containerization
    - Add database migration scripts
    - Create startup scripts for production

  - [x] 17.3 Add security hardening
    - Implement rate limiting for API endpoints
    - Add input sanitization for all user inputs
    - Configure CORS policies
    - Add security headers

- [ ] 18. Final checkpoint - Complete system validation
  - Run full test suite (unit + property + integration tests)
  - Verify all 69 correctness properties pass
  - Test with real anonymized medical reports
  - Perform security audit
  - Validate performance meets requirements
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP development
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties with 100+ iterations (1000+ for safety-critical properties)
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation builds on existing code in `ai_diet_planner/` directory
- Integration tests cover complete end-to-end workflows
- Performance tests ensure system meets timing requirements
- Security is integrated throughout (encryption, authentication, audit logging)
