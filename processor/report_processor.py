"""
Medical Report Processor

This module handles the acceptance and validation of medical reports in various formats.
It validates file size, format, and routes reports to appropriate processing pipelines.
"""

import io
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import BinaryIO, Dict, Optional, Union


# Type aliases
ReportID = str


class ProcessingStatus(Enum):
    """Status of report processing."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingPipeline(Enum):
    """Type of processing pipeline to use."""
    OCR_PDF = "ocr_pdf"
    OCR_IMAGE = "ocr_image"
    TEXT_DIRECT = "text_direct"


# Custom exceptions
class FileSizeError(Exception):
    """Raised when file exceeds maximum allowed size."""
    pass


class UnsupportedFormatError(Exception):
    """Raised when file format is not supported."""
    pass


@dataclass
class UploadedFile:
    """Represents an uploaded file."""
    filename: str
    content: bytes
    content_type: Optional[str] = None


@dataclass
class ReportMetadata:
    """Metadata for a medical report."""
    report_id: ReportID
    filename: str
    file_size: int
    format: str
    status: ProcessingStatus
    pipeline: Optional[ProcessingPipeline]
    uploaded_at: datetime
    error_message: Optional[str] = None


class MedicalReportProcessor:
    """
    Processes medical reports in multiple formats.
    
    Validates file size and format, then queues reports for processing.
    Supports PDF, JPEG, PNG, TIFF, and TXT formats with a 10MB size limit.
    """
    
    # Supported formats with their magic bytes
    SUPPORTED_FORMATS = {
        'pdf': {
            'extensions': ['.pdf'],
            'magic_bytes': [b'%PDF'],
            'mime_types': ['application/pdf']
        },
        'jpeg': {
            'extensions': ['.jpg', '.jpeg'],
            'magic_bytes': [b'\xff\xd8\xff'],
            'mime_types': ['image/jpeg']
        },
        'png': {
            'extensions': ['.png'],
            'magic_bytes': [b'\x89PNG\r\n\x1a\n'],
            'mime_types': ['image/png']
        },
        'tiff': {
            'extensions': ['.tif', '.tiff'],
            'magic_bytes': [b'II*\x00', b'MM\x00*'],  # Little-endian and big-endian
            'mime_types': ['image/tiff']
        },
        'txt': {
            'extensions': ['.txt'],
            'magic_bytes': [],  # Text files don't have magic bytes
            'mime_types': ['text/plain']
        }
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    def __init__(self):
        """Initialize the medical report processor."""
        self._processing_queue: Queue = Queue()
        self._report_metadata: Dict[ReportID, ReportMetadata] = {}
    
    def accept_report(self, file: UploadedFile) -> ReportID:
        """
        Accept a medical report file and queue for processing.
        
        Args:
            file: Uploaded file (PDF, image, or text)
            
        Returns:
            ReportID: Unique identifier for tracking processing status
            
        Raises:
            FileSizeError: If file exceeds 10MB
            UnsupportedFormatError: If file format not supported
        """
        # Validate file size
        file_size = len(file.content)
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeError(
                f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / (1024 * 1024):.0f}MB)"
            )
        
        # Detect and validate format
        detected_format = self._detect_format(file)
        if not detected_format:
            supported_formats = self._get_supported_formats_list()
            raise UnsupportedFormatError(
                f"Unsupported file format. Supported formats: {supported_formats}"
            )
        
        # Generate unique report ID
        report_id = self._generate_report_id()
        
        # Determine processing pipeline
        pipeline = self._determine_pipeline(detected_format)
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            filename=file.filename,
            file_size=file_size,
            format=detected_format,
            status=ProcessingStatus.QUEUED,
            pipeline=pipeline,
            uploaded_at=datetime.now()
        )
        
        # Store metadata
        self._report_metadata[report_id] = metadata
        
        # Queue for processing
        self._processing_queue.put((report_id, file))
        
        return report_id
    
    def get_processing_status(self, report_id: ReportID) -> ProcessingStatus:
        """
        Get current processing status of a report.
        
        Args:
            report_id: Unique report identifier
            
        Returns:
            ProcessingStatus: Current status of the report
            
        Raises:
            KeyError: If report_id not found
        """
        if report_id not in self._report_metadata:
            raise KeyError(f"Report ID {report_id} not found")
        
        return self._report_metadata[report_id].status
    
    def get_report_metadata(self, report_id: ReportID) -> ReportMetadata:
        """
        Get complete metadata for a report.
        
        Args:
            report_id: Unique report identifier
            
        Returns:
            ReportMetadata: Complete metadata for the report
            
        Raises:
            KeyError: If report_id not found
        """
        if report_id not in self._report_metadata:
            raise KeyError(f"Report ID {report_id} not found")
        
        return self._report_metadata[report_id]
    
    def route_to_pipeline(self, report_id: ReportID) -> ProcessingPipeline:
        """
        Determine appropriate processing pipeline based on file type.
        
        Args:
            report_id: Unique report identifier
            
        Returns:
            ProcessingPipeline: The pipeline to use for processing
            
        Raises:
            KeyError: If report_id not found
        """
        if report_id not in self._report_metadata:
            raise KeyError(f"Report ID {report_id} not found")
        
        metadata = self._report_metadata[report_id]
        if metadata.pipeline is None:
            raise ValueError(f"No pipeline determined for report {report_id}")
        
        return metadata.pipeline
    
    def update_status(
        self, 
        report_id: ReportID, 
        status: ProcessingStatus,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update the processing status of a report.
        
        Args:
            report_id: Unique report identifier
            status: New processing status
            error_message: Optional error message if status is FAILED
        """
        if report_id not in self._report_metadata:
            raise KeyError(f"Report ID {report_id} not found")
        
        self._report_metadata[report_id].status = status
        if error_message:
            self._report_metadata[report_id].error_message = error_message
    
    def get_next_report(self) -> Optional[tuple[ReportID, UploadedFile]]:
        """
        Get the next report from the processing queue.
        
        Returns:
            Tuple of (report_id, file) or None if queue is empty
        """
        if self._processing_queue.empty():
            return None
        
        return self._processing_queue.get()
    
    def _detect_format(self, file: UploadedFile) -> Optional[str]:
        """
        Detect file format using magic bytes and file extension.
        
        Args:
            file: Uploaded file to detect format for
            
        Returns:
            Format name (e.g., 'pdf', 'jpeg') or None if not supported
        """
        content = file.content
        filename = file.filename.lower()
        
        # Check each supported format
        for format_name, format_info in self.SUPPORTED_FORMATS.items():
            # Check magic bytes
            if format_info['magic_bytes']:
                for magic in format_info['magic_bytes']:
                    if content.startswith(magic):
                        return format_name
            
            # Check file extension as fallback
            for ext in format_info['extensions']:
                if filename.endswith(ext):
                    # For text files, verify it's actually text
                    if format_name == 'txt':
                        if self._is_text_file(content):
                            return format_name
                    else:
                        return format_name
        
        return None
    
    def _is_text_file(self, content: bytes) -> bool:
        """
        Check if content is a valid text file.
        
        Args:
            content: File content as bytes
            
        Returns:
            True if content is valid text, False otherwise
        """
        try:
            # Try to decode as UTF-8
            content.decode('utf-8')
            return True
        except UnicodeDecodeError:
            try:
                # Try to decode as ASCII
                content.decode('ascii')
                return True
            except UnicodeDecodeError:
                return False
    
    def _determine_pipeline(self, format: str) -> ProcessingPipeline:
        """
        Determine the appropriate processing pipeline for a format.
        
        Args:
            format: Detected file format
            
        Returns:
            ProcessingPipeline: The pipeline to use
        """
        if format == 'pdf':
            return ProcessingPipeline.OCR_PDF
        elif format in ['jpeg', 'png', 'tiff']:
            return ProcessingPipeline.OCR_IMAGE
        elif format == 'txt':
            return ProcessingPipeline.TEXT_DIRECT
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_report_id(self) -> ReportID:
        """
        Generate a unique report identifier.
        
        Returns:
            Unique report ID string
        """
        return str(uuid.uuid4())
    
    def _get_supported_formats_list(self) -> str:
        """
        Get a formatted string of supported formats.
        
        Returns:
            Comma-separated list of supported formats
        """
        formats = []
        for format_name, format_info in self.SUPPORTED_FORMATS.items():
            extensions = ', '.join(format_info['extensions'])
            formats.append(f"{format_name.upper()} ({extensions})")
        
        return '; '.join(formats)
