"""
Main Application Orchestrator for AI NutriCare System

This module wires all components together into a cohesive end-to-end pipeline:
- Medical Report Processor → OCR Engine → Data Extractor
- Data Extractor → ML Health Analyzer + NLP Text Interpreter
- Analyzers → Diet Plan Generator → Report Exporter → Data Store
- Backend integration with Streamlit UI

Validates: Requirements 2.4 and all integration requirements
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime

from .processor.report_processor import (
    MedicalReportProcessor,
    UploadedFile,
    ProcessingStatus,
    ProcessingPipeline,
    ReportID,
)
from .ocr.ocr_engine import OCREngine, UnreadableDocumentError
from .extraction.data_extractor import DataExtractor, InsufficientDataError
from .ml.health_analyzer import MLHealthAnalyzer
from .nlp.text_interpreter import NLPTextInterpreter
from .generation.diet_planner import DietPlanGenerator
from .export.report_exporter import ReportExporter
from .storage.data_store import DataStore
from .models import (
    StructuredHealthData,
    TextualNote,
    HealthCondition,
    Alert,
    DietRule,
    DietPlan,
    PatientProfile,
    UserPreferences,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineResult:
    """
    Result of processing a medical report through the complete pipeline.
    
    Attributes:
        report_id: Unique identifier for the report
        status: Processing status
        structured_data: Extracted health metrics (if successful)
        textual_notes: Extracted doctor notes (if successful)
        health_conditions: Detected health conditions (if successful)
        alerts: Health alerts (if successful)
        diet_rules: Extracted dietary rules (if successful)
        diet_plan: Generated diet plan (if successful)
        diet_plan_id: ID of saved diet plan (if successful)
        pdf_export: PDF bytes (if requested)
        json_export: JSON string (if requested)
        error_message: Error description (if failed)
        processing_time: Total processing time in seconds
    """
    
    def __init__(self, report_id: ReportID):
        self.report_id = report_id
        self.status = ProcessingStatus.QUEUED
        self.structured_data: Optional[StructuredHealthData] = None
        self.textual_notes: List[TextualNote] = []
        self.health_conditions: List[HealthCondition] = []
        self.alerts: List[Alert] = []
        self.diet_rules: List[DietRule] = []
        self.diet_plan: Optional[DietPlan] = None
        self.diet_plan_id: Optional[str] = None
        self.pdf_export: Optional[bytes] = None
        self.json_export: Optional[str] = None
        self.error_message: Optional[str] = None
        self.processing_time: float = 0.0
        self.start_time = datetime.now()
    
    def complete(self):
        """Mark processing as complete and calculate processing time."""
        self.status = ProcessingStatus.COMPLETED
        end_time = datetime.now()
        self.processing_time = (end_time - self.start_time).total_seconds()
    
    def fail(self, error_message: str):
        """Mark processing as failed with error message."""
        self.status = ProcessingStatus.FAILED
        self.error_message = error_message
        end_time = datetime.now()
        self.processing_time = (end_time - self.start_time).total_seconds()


class AINutriCareOrchestrator:
    """
    Main orchestrator that coordinates all components of the AI NutriCare System.
    
    This class implements the complete end-to-end pipeline from medical report
    upload through diet plan generation and storage.
    """
    
    def __init__(
        self,
        ocr_backend: str = "tesseract",
        nlp_model: Optional[str] = None,
        usda_api_key: Optional[str] = None,
        db_path: Optional[Path] = None,
        encryption_key: Optional[bytes] = None,
    ):
        """
        Initialize the orchestrator with all components.
        
        Args:
            ocr_backend: OCR engine to use ("tesseract" or "easyocr")
            nlp_model: NLP model to use ("groq", "gpt-4", "gpt-3.5-turbo", "bert")
                      If None, reads from NUTRICARE_NLP_MODEL env var (defaults to "groq")
            usda_api_key: Optional API key for USDA FoodData Central
            db_path: Optional path to database file (defaults to ./nutricare.db)
            encryption_key: Optional encryption key for data store (for testing)
        """
        logger.info("Initializing AI NutriCare Orchestrator...")
        
        # Get NLP model from environment if not specified
        if nlp_model is None:
            nlp_model = os.getenv("NUTRICARE_NLP_MODEL", "groq")
        
        # Initialize all components
        self.report_processor = MedicalReportProcessor()
        self.ocr_engine = OCREngine(backend=ocr_backend)
        self.data_extractor = DataExtractor()
        self.ml_analyzer = MLHealthAnalyzer()
        self.nlp_interpreter = NLPTextInterpreter(model=nlp_model)
        self.diet_generator = DietPlanGenerator(food_database_api_key=usda_api_key)
        self.report_exporter = ReportExporter()
        
        # Initialize data store
        if db_path is None:
            db_path = Path("./nutricare.db")
        self.data_store = DataStore(db_path=db_path, encryption_key=encryption_key)
        
        logger.info(f"All components initialized successfully (NLP: {nlp_model})")
    
    def process_report(
        self,
        uploaded_file: UploadedFile,
        patient_profile: Optional[PatientProfile] = None,
        user_preferences: Optional[UserPreferences] = None,
        export_pdf: bool = True,
        export_json: bool = False,
    ) -> PipelineResult:
        """
        Process a medical report through the complete pipeline.
        
        This method orchestrates the entire workflow:
        1. Accept and validate report
        2. Extract text via OCR (if needed)
        3. Extract structured data and textual notes
        4. Analyze health conditions (ML) and interpret notes (NLP)
        5. Generate personalized diet plan
        6. Export to PDF/JSON (if requested)
        7. Store in database
        
        Args:
            uploaded_file: The uploaded medical report file
            patient_profile: Optional patient information
            user_preferences: Optional dietary preferences and restrictions
            export_pdf: Whether to generate PDF export
            export_json: Whether to generate JSON export
        
        Returns:
            PipelineResult containing all outputs and status
        """
        result = None
        
        try:
            # Step 1: Accept report
            logger.info(f"Processing report: {uploaded_file.filename}")
            report_id = self.report_processor.accept_report(uploaded_file)
            result = PipelineResult(report_id)
            
            # Step 2: Extract text (OCR if needed)
            extracted_text = self._extract_text(report_id, uploaded_file)
            if not extracted_text:
                result.fail("Failed to extract text from report")
                return result
            
            # Step 3: Extract structured data and notes
            logger.info("Extracting structured data and textual notes...")
            try:
                result.structured_data = self.data_extractor.extract_structured_data(
                    extracted_text,
                    report_id
                )
            except InsufficientDataError as e:
                logger.warning(f"Insufficient structured data: {e}")
                result.fail(f"Could not extract health metrics: {e}")
                return result
            
            result.textual_notes = self.data_extractor.extract_textual_notes(extracted_text)
            
            # Step 4: Analyze health conditions (ML)
            logger.info("Analyzing health conditions with ML...")
            metrics_dict = self._convert_metrics_to_dict(result.structured_data)
            result.health_conditions = self.ml_analyzer.classify_conditions(metrics_dict)
            result.alerts = self.ml_analyzer.detect_abnormal_values(metrics_dict)
            
            # Step 5: Interpret notes (NLP)
            logger.info("Interpreting textual notes with NLP...")
            if result.textual_notes:
                result.diet_rules = self.nlp_interpreter.interpret_notes(result.textual_notes)
            else:
                logger.warning("No textual notes found, using ML-based rules only")
                result.diet_rules = []
            
            # Step 6: Generate diet plan
            logger.info("Generating personalized diet plan...")
            if user_preferences is None:
                user_preferences = UserPreferences(
                    dietary_style=None,
                    allergies=[],
                    dislikes=[],
                    cultural_preferences=[]
                )
            
            # Create default patient profile if not provided
            if patient_profile is None:
                # Use default values for diet plan generation
                logger.info("No patient profile provided, using defaults")
                import uuid
                patient_profile = PatientProfile(
                    patient_id=f"patient_{uuid.uuid4().hex[:12]}",
                    age=30,
                    gender="Male",
                    height_cm=170,
                    weight_kg=70,
                    activity_level="moderate",
                    preferences=user_preferences,
                    created_at=None
                )
            
            try:
                result.diet_plan = self.diet_generator.generate_plan(
                    patient_profile=patient_profile,
                    health_conditions=result.health_conditions,
                    diet_rules=result.diet_rules,
                    preferences=user_preferences
                )
                logger.info("Diet plan generated successfully")
            except Exception as diet_error:
                logger.error(f"Diet plan generation failed: {diet_error}", exc_info=True)
                result.fail(f"Failed to generate diet plan: {diet_error}")
                return result
            
            # Step 7: Export to PDF/JSON
            if export_pdf:
                logger.info("Exporting diet plan to PDF...")
                result.pdf_export = self.report_exporter.export_pdf(
                    result.diet_plan,
                    patient_profile
                )
            
            if export_json:
                logger.info("Exporting diet plan to JSON...")
                result.json_export = self.report_exporter.export_json(result.diet_plan)
            
            # Step 8: Store in database
            logger.info("Storing data in database...")
            if patient_profile:
                # Generate unique patient ID if empty
                if not patient_profile.patient_id:
                    import uuid
                    patient_profile.patient_id = f"patient_{uuid.uuid4().hex[:12]}"
                
                try:
                    patient_id = self.data_store.save_patient(patient_profile)
                    result.diet_plan_id = self.data_store.save_diet_plan(
                        patient_id,
                        result.diet_plan
                    )
                except Exception as db_error:
                    logger.warning(f"Database storage failed: {db_error}")
                    # Continue without database storage - don't fail the whole pipeline
            else:
                logger.warning("No patient profile provided, skipping database storage")
            
            # Mark as complete
            result.complete()
            logger.info(f"Report processed successfully in {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            if result is None:
                result = PipelineResult("unknown")
            result.fail(str(e))
            return result
    
    def _extract_text(self, report_id: ReportID, uploaded_file: UploadedFile) -> Optional[str]:
        """
        Extract text from uploaded file using appropriate method.
        
        Args:
            report_id: Report identifier
            uploaded_file: The uploaded file
        
        Returns:
            Extracted text or None if extraction failed
        """
        # Determine processing pipeline
        pipeline = self.report_processor.route_to_pipeline(report_id)
        
        try:
            if pipeline == ProcessingPipeline.TEXT_DIRECT:
                # Direct text input
                logger.info("Processing direct text input")
                return uploaded_file.content.decode('utf-8')
            
            elif pipeline == ProcessingPipeline.OCR_PDF:
                # PDF OCR
                logger.info("Extracting text from PDF via OCR")
                # Save to temporary file for OCR processing
                temp_path = Path(f"/tmp/{report_id}.pdf")
                temp_path.write_bytes(uploaded_file.content)
                
                try:
                    ocr_result = self.ocr_engine.extract_text_from_pdf(temp_path)
                    return ocr_result.full_text
                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
            
            elif pipeline == ProcessingPipeline.OCR_IMAGE:
                # Image OCR
                logger.info("Extracting text from image via OCR")
                # Save to temporary file for OCR processing
                temp_path = Path(f"/tmp/{report_id}.img")
                temp_path.write_bytes(uploaded_file.content)
                
                try:
                    ocr_result = self.ocr_engine.extract_text_from_image(temp_path)
                    return ocr_result.full_text
                finally:
                    # Clean up temp file
                    if temp_path.exists():
                        temp_path.unlink()
            
            else:
                logger.error(f"Unknown pipeline type: {pipeline}")
                return None
                
        except UnreadableDocumentError as e:
            logger.error(f"OCR failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Text extraction failed: {e}", exc_info=True)
            return None
    
    def _convert_metrics_to_dict(self, structured_data: StructuredHealthData) -> Dict[str, float]:
        """
        Convert StructuredHealthData to dictionary format for ML analyzer.
        
        Args:
            structured_data: Extracted health metrics
        
        Returns:
            Dictionary mapping metric names to values
        """
        metrics_dict = {}
        
        for metric in structured_data.metrics:
            # Convert MetricType enum to string key
            metric_name = metric.metric_type.value
            
            # Map to ML analyzer expected keys
            key_mapping = {
                'glucose': 'Glucose',
                'cholesterol_total': 'Cholesterol',
                'cholesterol_ldl': 'LDL',
                'cholesterol_hdl': 'HDL',
                'triglycerides': 'Triglycerides',
                'bmi': 'BMI',
                'bp_systolic': 'BloodPressure',
                'bp_diastolic': 'DiastolicBP',
                'hemoglobin': 'Hemoglobin',
                'hba1c': 'HbA1c',
            }
            
            ml_key = key_mapping.get(metric_name, metric_name)
            metrics_dict[ml_key] = metric.value
        
        return metrics_dict
    
    def get_patient_history(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve complete patient history from database.
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            Dictionary containing patient profile, reports, and diet plans
        """
        logger.info(f"Retrieving history for patient {patient_id}")
        return self.data_store.get_patient_history(patient_id)
    
    def delete_patient_data(self, patient_id: str) -> bool:
        """
        Permanently delete all patient data.
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            True if deletion successful, False otherwise
        """
        logger.info(f"Deleting data for patient {patient_id}")
        return self.data_store.delete_patient_data(patient_id)
    
    def get_processing_status(self, report_id: ReportID) -> ProcessingStatus:
        """
        Get current processing status of a report.
        
        Args:
            report_id: Report identifier
        
        Returns:
            Current processing status
        """
        return self.report_processor.get_processing_status(report_id)


# Convenience function for simple usage
def process_medical_report(
    file_path: Path,
    patient_profile: Optional[PatientProfile] = None,
    user_preferences: Optional[UserPreferences] = None,
    encryption_key: Optional[bytes] = None,
) -> PipelineResult:
    """
    Convenience function to process a medical report file.
    
    Args:
        file_path: Path to medical report file
        patient_profile: Optional patient information
        user_preferences: Optional dietary preferences
        encryption_key: Optional encryption key for data store
    
    Returns:
        PipelineResult with all outputs
    """
    # Read file
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Create uploaded file
    uploaded_file = UploadedFile(
        filename=file_path.name,
        content=content
    )
    
    # Create orchestrator and process
    orchestrator = AINutriCareOrchestrator(encryption_key=encryption_key)
    return orchestrator.process_report(
        uploaded_file,
        patient_profile,
        user_preferences
    )


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m ai_diet_planner.main <report_file>")
        sys.exit(1)
    
    report_path = Path(sys.argv[1])
    if not report_path.exists():
        print(f"Error: File not found: {report_path}")
        sys.exit(1)
    
    print(f"Processing medical report: {report_path}")
    result = process_medical_report(report_path)
    
    if result.status == ProcessingStatus.COMPLETED:
        print(f"\n✓ Processing completed in {result.processing_time:.2f}s")
        print(f"\nHealth Conditions Detected: {len(result.health_conditions)}")
        for condition in result.health_conditions:
            print(f"  - {condition.condition_type.value}: {condition.confidence:.2%}")
        
        print(f"\nAlerts Generated: {len(result.alerts)}")
        for alert in result.alerts:
            print(f"  - {alert.severity.value.upper()}: {alert.message}")
        
        print(f"\nDiet Rules Extracted: {len(result.diet_rules)}")
        
        if result.diet_plan:
            print(f"\nDiet Plan Generated:")
            print(f"  Daily Calories: {result.diet_plan.daily_calories:.0f}")
            print(f"  Meals: {len(result.diet_plan.meals)}")
    else:
        print(f"\n✗ Processing failed: {result.error_message}")
        sys.exit(1)
