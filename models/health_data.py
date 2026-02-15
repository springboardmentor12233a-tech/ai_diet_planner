"""
Health data models for the AI NutriCare System.

This module contains data classes for health metrics, medical conditions,
alerts, and extracted health data from medical reports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .enums import MetricType, AlertSeverity, ConditionType


@dataclass
class HealthMetric:
    """
    A single health metric extracted from a medical report.
    
    Attributes:
        metric_type: The type of health metric (glucose, cholesterol, etc.)
        value: The numeric value of the metric
        unit: The unit of measurement (mg/dL, mmol/L, etc.)
        extracted_at: Timestamp when the metric was extracted
        confidence: OCR confidence score (0.0 to 1.0)
    """
    
    metric_type: MetricType
    value: float
    unit: str
    extracted_at: datetime
    confidence: float


@dataclass
class StructuredHealthData:
    """
    Collection of structured health metrics extracted from a medical report.
    
    Attributes:
        metrics: List of extracted health metrics
        report_id: Unique identifier for the source medical report
        extraction_timestamp: When the extraction was completed
    """
    
    metrics: List[HealthMetric]
    report_id: str
    extraction_timestamp: datetime


@dataclass
class TextualNote:
    """
    A textual note extracted from a medical report.
    
    Attributes:
        content: The text content of the note
        section: The section type (doctor_notes, prescription, recommendation)
        page_number: Optional page number where the note was found
    """
    
    content: str
    section: str
    page_number: Optional[int] = None


@dataclass
class Alert:
    """
    An alert generated for an abnormal health metric value.
    
    Attributes:
        metric_type: The type of metric that triggered the alert
        severity: The severity level of the alert
        message: Human-readable alert message
        recommended_action: Optional recommended action to take
    """
    
    metric_type: MetricType
    severity: AlertSeverity
    message: str
    recommended_action: Optional[str] = None


@dataclass
class HealthCondition:
    """
    A health condition detected by ML analysis.
    
    Attributes:
        condition_type: The type of health condition detected
        confidence: ML model confidence score (0.0 to 1.0)
        detected_at: Timestamp when the condition was detected
        contributing_metrics: List of metrics that contributed to detection
    """
    
    condition_type: ConditionType
    confidence: float
    contributing_metrics: List[MetricType]
    detected_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set detected_at to current time if not provided."""
        if self.detected_at is None:
            self.detected_at = datetime.now()
