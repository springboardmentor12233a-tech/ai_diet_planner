"""
Unit tests for Medical Report Processor

Tests file validation, format detection, and processing queue functionality.
"""

import pytest
from .report_processor import (
    MedicalReportProcessor,
    UploadedFile,
    ProcessingStatus,
    ProcessingPipeline,
    FileSizeError,
    UnsupportedFormatError,
)


class TestMedicalReportProcessor:
    """Test suite for MedicalReportProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh processor instance for each test."""
        return MedicalReportProcessor()
    
    # Test valid file acceptance
    
    def test_accept_valid_pdf(self, processor):
        """Test accepting a valid PDF file."""
        file = UploadedFile(
            filename="report.pdf",
            content=b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n" + b"x" * 100,
            content_type="application/pdf"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert isinstance(report_id, str)
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_PDF
    
    def test_accept_valid_jpeg(self, processor):
        """Test accepting a valid JPEG file."""
        file = UploadedFile(
            filename="scan.jpg",
            content=b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"x" * 100,
            content_type="image/jpeg"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_IMAGE
    
    def test_accept_valid_png(self, processor):
        """Test accepting a valid PNG file."""
        file = UploadedFile(
            filename="report.png",
            content=b"\x89PNG\r\n\x1a\n" + b"x" * 100,
            content_type="image/png"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_IMAGE
    
    def test_accept_valid_tiff_little_endian(self, processor):
        """Test accepting a valid TIFF file (little-endian)."""
        file = UploadedFile(
            filename="scan.tiff",
            content=b"II*\x00" + b"x" * 100,
            content_type="image/tiff"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_IMAGE
    
    def test_accept_valid_tiff_big_endian(self, processor):
        """Test accepting a valid TIFF file (big-endian)."""
        file = UploadedFile(
            filename="scan.tif",
            content=b"MM\x00*" + b"x" * 100,
            content_type="image/tiff"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_IMAGE
    
    def test_accept_valid_txt(self, processor):
        """Test accepting a valid text file."""
        file = UploadedFile(
            filename="report.txt",
            content=b"Patient Name: John Doe\nBlood Sugar: 120 mg/dL",
            content_type="text/plain"
        )
        
        report_id = processor.accept_report(file)
        
        assert report_id is not None
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.TEXT_DIRECT
    
    # Test file size validation
    
    def test_reject_oversized_file(self, processor):
        """Test rejecting a file that exceeds 10MB."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file = UploadedFile(
            filename="large_report.pdf",
            content=b"%PDF-1.4\n" + large_content,
            content_type="application/pdf"
        )
        
        with pytest.raises(FileSizeError) as exc_info:
            processor.accept_report(file)
        
        assert "exceeds maximum allowed size" in str(exc_info.value)
        assert "10MB" in str(exc_info.value)
    
    def test_accept_file_at_size_limit(self, processor):
        """Test accepting a file exactly at the 10MB limit."""
        # Create a file exactly 10MB
        content = b"x" * (10 * 1024 * 1024 - 10)  # Account for PDF header
        file = UploadedFile(
            filename="max_size.pdf",
            content=b"%PDF-1.4\n" + content,
            content_type="application/pdf"
        )
        
        report_id = processor.accept_report(file)
        assert report_id is not None
    
    # Test unsupported format rejection
    
    def test_reject_unsupported_format_docx(self, processor):
        """Test rejecting an unsupported DOCX file."""
        file = UploadedFile(
            filename="report.docx",
            content=b"PK\x03\x04" + b"x" * 100,  # DOCX magic bytes
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        with pytest.raises(UnsupportedFormatError) as exc_info:
            processor.accept_report(file)
        
        error_message = str(exc_info.value)
        assert "Unsupported file format" in error_message
        assert "PDF" in error_message
        assert "JPEG" in error_message
        assert "PNG" in error_message
        assert "TIFF" in error_message
        assert "TXT" in error_message
    
    def test_reject_unsupported_format_xlsx(self, processor):
        """Test rejecting an unsupported XLSX file."""
        file = UploadedFile(
            filename="data.xlsx",
            content=b"PK\x03\x04" + b"x" * 100,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        with pytest.raises(UnsupportedFormatError) as exc_info:
            processor.accept_report(file)
        
        assert "Supported formats:" in str(exc_info.value)
    
    def test_reject_binary_file_with_txt_extension(self, processor):
        """Test rejecting a binary file with .txt extension."""
        file = UploadedFile(
            filename="fake.txt",
            content=b"\x00\x01\x02\x03\x04\x05" + b"\xff" * 100,  # Binary data
            content_type="text/plain"
        )
        
        with pytest.raises(UnsupportedFormatError):
            processor.accept_report(file)
    
    # Test format detection
    
    def test_format_detection_by_magic_bytes(self, processor):
        """Test format detection prioritizes magic bytes over extension."""
        # PDF content with wrong extension
        file = UploadedFile(
            filename="report.txt",  # Wrong extension
            content=b"%PDF-1.4\n" + b"x" * 100,
            content_type="text/plain"
        )
        
        report_id = processor.accept_report(file)
        
        # Should detect as PDF based on magic bytes
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_PDF
    
    def test_format_detection_by_extension_fallback(self, processor):
        """Test format detection falls back to extension for text files."""
        file = UploadedFile(
            filename="report.txt",
            content=b"Plain text medical report",
            content_type="text/plain"
        )
        
        report_id = processor.accept_report(file)
        
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.TEXT_DIRECT
    
    # Test processing queue
    
    def test_processing_queue_order(self, processor):
        """Test that reports are queued in FIFO order."""
        file1 = UploadedFile(
            filename="report1.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        file2 = UploadedFile(
            filename="report2.pdf",
            content=b"%PDF-1.4\n" + b"y" * 100
        )
        
        id1 = processor.accept_report(file1)
        id2 = processor.accept_report(file2)
        
        # Get reports from queue
        next_report = processor.get_next_report()
        assert next_report is not None
        assert next_report[0] == id1
        
        next_report = processor.get_next_report()
        assert next_report is not None
        assert next_report[0] == id2
        
        # Queue should be empty now
        assert processor.get_next_report() is None
    
    def test_empty_queue(self, processor):
        """Test getting from empty queue returns None."""
        assert processor.get_next_report() is None
    
    # Test status management
    
    def test_update_status(self, processor):
        """Test updating report processing status."""
        file = UploadedFile(
            filename="report.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        report_id = processor.accept_report(file)
        
        # Initial status should be QUEUED
        assert processor.get_processing_status(report_id) == ProcessingStatus.QUEUED
        
        # Update to PROCESSING
        processor.update_status(report_id, ProcessingStatus.PROCESSING)
        assert processor.get_processing_status(report_id) == ProcessingStatus.PROCESSING
        
        # Update to COMPLETED
        processor.update_status(report_id, ProcessingStatus.COMPLETED)
        assert processor.get_processing_status(report_id) == ProcessingStatus.COMPLETED
    
    def test_update_status_with_error(self, processor):
        """Test updating status with error message."""
        file = UploadedFile(
            filename="report.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        report_id = processor.accept_report(file)
        
        error_msg = "OCR extraction failed: insufficient image quality"
        processor.update_status(report_id, ProcessingStatus.FAILED, error_msg)
        
        assert processor.get_processing_status(report_id) == ProcessingStatus.FAILED
        metadata = processor.get_report_metadata(report_id)
        assert metadata.error_message == error_msg
    
    def test_get_status_invalid_id(self, processor):
        """Test getting status for non-existent report ID."""
        with pytest.raises(KeyError):
            processor.get_processing_status("invalid-id")
    
    # Test metadata retrieval
    
    def test_get_report_metadata(self, processor):
        """Test retrieving complete report metadata."""
        file = UploadedFile(
            filename="test_report.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        report_id = processor.accept_report(file)
        metadata = processor.get_report_metadata(report_id)
        
        assert metadata.report_id == report_id
        assert metadata.filename == "test_report.pdf"
        assert metadata.format == "pdf"
        assert metadata.status == ProcessingStatus.QUEUED
        assert metadata.pipeline == ProcessingPipeline.OCR_PDF
        assert metadata.file_size > 0
        assert metadata.uploaded_at is not None
    
    def test_get_metadata_invalid_id(self, processor):
        """Test getting metadata for non-existent report ID."""
        with pytest.raises(KeyError):
            processor.get_report_metadata("invalid-id")
    
    # Test unique report IDs
    
    def test_unique_report_ids(self, processor):
        """Test that each report gets a unique ID."""
        file = UploadedFile(
            filename="report.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        id1 = processor.accept_report(file)
        id2 = processor.accept_report(file)
        id3 = processor.accept_report(file)
        
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3
    
    # Test edge cases
    
    def test_empty_file(self, processor):
        """Test handling of empty file."""
        file = UploadedFile(
            filename="empty.txt",
            content=b"",
            content_type="text/plain"
        )
        
        # Empty file is valid UTF-8, so it should be accepted as text
        report_id = processor.accept_report(file)
        assert report_id is not None
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.TEXT_DIRECT
    
    def test_file_with_multiple_extensions(self, processor):
        """Test file with multiple extensions."""
        file = UploadedFile(
            filename="report.backup.pdf",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        report_id = processor.accept_report(file)
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_PDF
    
    def test_case_insensitive_extension(self, processor):
        """Test that extension matching is case-insensitive."""
        file = UploadedFile(
            filename="REPORT.PDF",
            content=b"%PDF-1.4\n" + b"x" * 100
        )
        
        report_id = processor.accept_report(file)
        assert processor.route_to_pipeline(report_id) == ProcessingPipeline.OCR_PDF
