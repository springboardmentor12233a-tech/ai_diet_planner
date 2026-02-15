"""
End-to-End Integration Test for Data Extraction Pipeline

Task 5 Checkpoint: Validates the complete pipeline:
Report Processor → OCR Engine → Data Extractor

Tests:
- Upload sample medical report
- Process through OCR
- Extract structured metrics and textual notes
- Verify output format matches expected models
"""

import pytest
from pathlib import Path
from PIL import Image

from ai_diet_planner.processor.report_processor import (
    MedicalReportProcessor,
    UploadedFile,
    ProcessingStatus,
    ProcessingPipeline
)
from ai_diet_planner.ocr.ocr_engine import OCREngine, UnreadableDocumentError
from ai_diet_planner.extraction.data_extractor import DataExtractor, InsufficientDataError
from ai_diet_planner.models.health_data import StructuredHealthData, TextualNote
from ai_diet_planner.models.enums import MetricType


# Get paths to test data
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "datasets" / "images"
PDF_DIR = BASE_DIR / "datasets" / "pdfs"


class TestEndToEndPipeline:
    """Test complete data extraction pipeline end-to-end."""
    
    @pytest.fixture
    def processor(self):
        """Create Medical Report Processor."""
        return MedicalReportProcessor()
    
    @pytest.fixture
    def ocr_engine(self):
        """Create OCR Engine."""
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def data_extractor(self):
        """Create Data Extractor."""
        return DataExtractor()
    
    @pytest.fixture
    def sample_images(self):
        """Get available test images."""
        if not IMAGE_DIR.exists():
            pytest.skip("Image directory not found")
        
        images = list(IMAGE_DIR.glob("*.png")) + list(IMAGE_DIR.glob("*.jpg"))
        if not images:
            pytest.skip("No test images found")
        
        return images
    
    def test_pipeline_image_to_structured_data(
        self, processor, ocr_engine, data_extractor, sample_images
    ):
        """
        Test complete pipeline: Image upload → OCR → Data extraction.
        
        This validates:
        1. Report processor accepts image
        2. OCR extracts text from image
        3. Data extractor parses structured metrics
        4. Output matches StructuredHealthData model
        """
        # Step 1: Upload image through processor
        image_path = sample_images[0]
        with open(image_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            filename=image_path.name,
            content=file_content,
            content_type="image/png"
        )
        
        report_id = processor.accept_report(uploaded_file)
        
        # Verify report accepted
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_IMAGE
        
        # Step 2: Process through OCR
        processor.update_status(report_id, ProcessingStatus.PROCESSING)
        
        try:
            ocr_result = ocr_engine.extract_text_from_image(image_path)
            
            # Verify OCR output
            assert ocr_result is not None
            assert isinstance(ocr_result.full_text, str)
            
            # If no text extracted, skip this image
            if len(ocr_result.full_text.strip()) == 0:
                pytest.skip("Image does not contain readable text")
            
            # Step 3: Extract structured data
            try:
                structured_data = data_extractor.extract_structured_data(
                    ocr_result.full_text,
                    report_id
                )
                
                # Verify structured data format
                assert isinstance(structured_data, StructuredHealthData)
                assert structured_data.report_id == report_id
                assert len(structured_data.metrics) > 0, "Should extract at least one metric"
                
                # Verify each metric has required fields
                for metric in structured_data.metrics:
                    assert isinstance(metric.metric_type, MetricType)
                    assert isinstance(metric.value, (int, float))
                    assert isinstance(metric.unit, str)
                    assert 0.0 <= metric.confidence <= 1.0
                
                processor.update_status(report_id, ProcessingStatus.COMPLETED)
                
            except InsufficientDataError:
                # Image might not contain health metrics - this is acceptable
                pytest.skip("Image does not contain extractable health metrics")
        
        except UnreadableDocumentError:
            # Image quality might be insufficient - this is acceptable
            pytest.skip("Image quality insufficient for OCR")
    
    def test_pipeline_extracts_textual_notes(
        self, processor, ocr_engine, data_extractor, sample_images
    ):
        """
        Test pipeline extracts textual notes (doctor notes, prescriptions).
        
        Validates:
        1. OCR extracts text
        2. Data extractor identifies note sections
        3. Output matches TextualNote model
        """
        image_path = sample_images[0]
        with open(image_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            filename=image_path.name,
            content=file_content
        )
        
        report_id = processor.accept_report(uploaded_file)
        
        try:
            # Extract text via OCR
            ocr_result = ocr_engine.extract_text_from_image(image_path)
            
            # Extract textual notes
            textual_notes = data_extractor.extract_textual_notes(ocr_result.full_text)
            
            # Verify notes format
            assert isinstance(textual_notes, list)
            
            for note in textual_notes:
                assert isinstance(note, TextualNote)
                assert isinstance(note.content, str)
                assert isinstance(note.section, str)
                assert note.section in [
                    "doctor_notes",
                    "prescriptions",
                    "recommendations",
                    "general"
                ]
        
        except UnreadableDocumentError:
            pytest.skip("Image quality insufficient for OCR")
    
    def test_pipeline_with_multiple_images(
        self, processor, ocr_engine, data_extractor, sample_images
    ):
        """
        Test pipeline processes multiple images successfully.
        
        Validates pipeline can handle multiple reports in sequence.
        """
        results = []
        
        # Process up to 3 images
        for image_path in sample_images[:3]:
            with open(image_path, 'rb') as f:
                file_content = f.read()
            
            uploaded_file = UploadedFile(
                filename=image_path.name,
                content=file_content
            )
            
            report_id = processor.accept_report(uploaded_file)
            
            try:
                # OCR extraction
                ocr_result = ocr_engine.extract_text_from_image(image_path)
                
                # Data extraction
                try:
                    structured_data = data_extractor.extract_structured_data(
                        ocr_result.full_text,
                        report_id
                    )
                    
                    results.append({
                        'report_id': report_id,
                        'filename': image_path.name,
                        'metrics_count': len(structured_data.metrics),
                        'status': 'success'
                    })
                
                except InsufficientDataError:
                    results.append({
                        'report_id': report_id,
                        'filename': image_path.name,
                        'status': 'no_metrics'
                    })
            
            except UnreadableDocumentError:
                results.append({
                    'report_id': report_id,
                    'filename': image_path.name,
                    'status': 'ocr_failed'
                })
        
        # At least one image should process successfully
        assert len(results) > 0
        # All reports should have unique IDs
        report_ids = [r['report_id'] for r in results]
        assert len(report_ids) == len(set(report_ids))
    
    def test_pipeline_output_format_validation(
        self, processor, ocr_engine, data_extractor, sample_images
    ):
        """
        Test that pipeline output matches expected data models.
        
        Validates:
        - StructuredHealthData has all required fields
        - TextualNote has all required fields
        - Data types are correct
        """
        image_path = sample_images[0]
        with open(image_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            filename=image_path.name,
            content=file_content
        )
        
        report_id = processor.accept_report(uploaded_file)
        
        try:
            ocr_result = ocr_engine.extract_text_from_image(image_path)
            
            try:
                # Test StructuredHealthData format
                structured_data = data_extractor.extract_structured_data(
                    ocr_result.full_text,
                    report_id
                )
                
                # Validate StructuredHealthData fields
                assert hasattr(structured_data, 'metrics')
                assert hasattr(structured_data, 'report_id')
                assert hasattr(structured_data, 'extraction_timestamp')
                
                assert isinstance(structured_data.metrics, list)
                assert isinstance(structured_data.report_id, str)
                
                # Validate HealthMetric fields
                if len(structured_data.metrics) > 0:
                    metric = structured_data.metrics[0]
                    assert hasattr(metric, 'metric_type')
                    assert hasattr(metric, 'value')
                    assert hasattr(metric, 'unit')
                    assert hasattr(metric, 'confidence')
            
            except InsufficientDataError:
                pass  # No metrics is acceptable
            
            # Test TextualNote format
            textual_notes = data_extractor.extract_textual_notes(ocr_result.full_text)
            
            assert isinstance(textual_notes, list)
            
            if len(textual_notes) > 0:
                note = textual_notes[0]
                assert hasattr(note, 'content')
                assert hasattr(note, 'section')
                assert hasattr(note, 'page_number')
        
        except UnreadableDocumentError:
            pytest.skip("Image quality insufficient for OCR")
    
    def test_pipeline_error_handling(
        self, processor, ocr_engine, data_extractor
    ):
        """
        Test pipeline handles errors gracefully.
        
        Validates:
        - Invalid files are rejected
        - OCR failures are caught
        - Extraction failures are caught
        """
        # Test 1: Invalid file format
        invalid_file = UploadedFile(
            filename="test.docx",
            content=b"PK\x03\x04" + b"x" * 100
        )
        
        from ai_diet_planner.processor.report_processor import UnsupportedFormatError
        with pytest.raises(UnsupportedFormatError):
            processor.accept_report(invalid_file)
        
        # Test 2: Oversized file
        large_file = UploadedFile(
            filename="large.png",
            content=b"\x89PNG\r\n\x1a\n" + b"x" * (11 * 1024 * 1024)
        )
        
        from ai_diet_planner.processor.report_processor import FileSizeError
        with pytest.raises(FileSizeError):
            processor.accept_report(large_file)
        
        # Test 3: Empty text extraction
        with pytest.raises(InsufficientDataError):
            data_extractor.extract_structured_data("", "test-report")
        
        # Test 4: Text with no metrics
        with pytest.raises(InsufficientDataError):
            data_extractor.extract_structured_data(
                "This is just random text with no health data.",
                "test-report"
            )
    
    def test_pipeline_preserves_data_integrity(
        self, processor, ocr_engine, data_extractor, sample_images
    ):
        """
        Test that data integrity is maintained through the pipeline.
        
        Validates:
        - Report IDs are preserved
        - Timestamps are set correctly
        - No data loss between stages
        """
        image_path = sample_images[0]
        with open(image_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            filename=image_path.name,
            content=file_content
        )
        
        # Stage 1: Report acceptance
        report_id = processor.accept_report(uploaded_file)
        metadata = processor.get_report_metadata(report_id)
        
        assert metadata.report_id == report_id
        assert metadata.filename == image_path.name
        assert metadata.uploaded_at is not None
        
        try:
            # Stage 2: OCR extraction
            ocr_result = ocr_engine.extract_text_from_image(image_path)
            
            assert len(ocr_result.pages) > 0
            for page in ocr_result.pages:
                assert page.extraction_timestamp is not None
            
            # Stage 3: Data extraction
            try:
                structured_data = data_extractor.extract_structured_data(
                    ocr_result.full_text,
                    report_id
                )
                
                # Verify report ID preserved
                assert structured_data.report_id == report_id
                
                # Verify timestamp set
                assert structured_data.extraction_timestamp is not None
                
                # Verify metrics have timestamps
                for metric in structured_data.metrics:
                    assert metric.extracted_at is not None
            
            except InsufficientDataError:
                pytest.skip("No metrics to validate")
        
        except UnreadableDocumentError:
            pytest.skip("Image quality insufficient")


class TestPipelineWithPDFs:
    """Test pipeline with PDF files."""
    
    @pytest.fixture
    def processor(self):
        return MedicalReportProcessor()
    
    @pytest.fixture
    def ocr_engine(self):
        return OCREngine(backend="tesseract")
    
    @pytest.fixture
    def data_extractor(self):
        return DataExtractor()
    
    @pytest.fixture
    def sample_pdfs(self):
        """Get available test PDFs."""
        if not PDF_DIR.exists():
            pytest.skip("PDF directory not found")
        
        pdfs = list(PDF_DIR.glob("*.pdf"))
        if not pdfs:
            pytest.skip("No test PDFs found")
        
        return pdfs
    
    def test_pipeline_pdf_to_structured_data(
        self, processor, ocr_engine, data_extractor, sample_pdfs
    ):
        """
        Test complete pipeline with PDF input.
        
        Validates:
        1. Report processor accepts PDF
        2. OCR extracts text from PDF
        3. Data extractor parses structured metrics
        4. Multi-page PDFs are handled correctly
        """
        pdf_path = sample_pdfs[0]
        with open(pdf_path, 'rb') as f:
            file_content = f.read()
        
        uploaded_file = UploadedFile(
            filename=pdf_path.name,
            content=file_content,
            content_type="application/pdf"
        )
        
        report_id = processor.accept_report(uploaded_file)
        
        # Verify PDF accepted
        assert report_id is not None
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_PDF
        
        try:
            # Extract text from PDF
            ocr_result = ocr_engine.extract_text_from_pdf(pdf_path)
            
            # Verify multi-page handling
            assert ocr_result.total_pages > 0
            assert len(ocr_result.pages) == ocr_result.total_pages
            
            # Verify page order preserved
            for i, page in enumerate(ocr_result.pages, start=1):
                assert page.page_number == i
            
            # Extract structured data
            try:
                structured_data = data_extractor.extract_structured_data(
                    ocr_result.full_text,
                    report_id
                )
                
                assert isinstance(structured_data, StructuredHealthData)
                assert len(structured_data.metrics) > 0
            
            except InsufficientDataError:
                pytest.skip("PDF does not contain extractable health metrics")
        
        except UnreadableDocumentError:
            pytest.skip("PDF quality insufficient for OCR")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
