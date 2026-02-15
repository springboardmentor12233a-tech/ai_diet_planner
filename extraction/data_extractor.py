"""
Data extraction module for parsing medical report text.

This module provides the DataExtractor class which uses regex patterns and
context analysis to extract structured health metrics and textual notes from
medical report text.
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from ..models.health_data import HealthMetric, StructuredHealthData, TextualNote
from ..models.enums import MetricType


@dataclass
class ExtractionResult:
    """Result of data extraction containing both structured and textual data."""
    structured_data: StructuredHealthData
    textual_notes: List[TextualNote]
    ambiguous_values: List[Dict[str, any]]


class InsufficientDataError(Exception):
    """Raised when no health metrics can be extracted from text."""
    pass


class DataExtractor:
    """
    Extracts structured health metrics and textual notes from medical report text.
    
    This class uses regex patterns to identify health metrics, performs unit
    normalization, disambiguates metric types using context analysis, detects
    different sections of medical reports, and flags ambiguous values.
    """
    
    def __init__(self):
        """Initialize the DataExtractor with regex patterns and unit conversions."""
        self._init_patterns()
        self._init_unit_conversions()
        self._init_section_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns for health metric extraction."""
        # Glucose patterns
        self.patterns = {
            MetricType.GLUCOSE: [
                r'(?:glucose|blood\s+sugar|fasting\s+glucose|fbs|ppbs|random\s+glucose)\s*(?:\([^)]*\))?\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                r'(?:glucose|sugar)\s*(?:\([^)]*\))?\s*[:\-]?\s*(\d+\.?\d*)',
            ],
            MetricType.CHOLESTEROL_TOTAL: [
                r'(?:total\s+cholesterol|cholesterol\s+total|t\.?\s*chol)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                r'(?:cholesterol)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
            ],
            MetricType.CHOLESTEROL_LDL: [
                r'(?:ldl|ldl\s+cholesterol|low\s+density\s+lipoprotein)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
            ],
            MetricType.CHOLESTEROL_HDL: [
                r'(?:hdl|hdl\s+cholesterol|high\s+density\s+lipoprotein)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
            ],
            MetricType.TRIGLYCERIDES: [
                r'(?:triglycerides?|tg)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
            ],
            MetricType.BMI: [
                r'(?:bmi|body\s+mass\s+index)\s*[:\-]?\s*(\d+\.?\d*)',
            ],
            MetricType.BLOOD_PRESSURE_SYSTOLIC: [
                r'(?:bp|blood\s+pressure)\s*[:\-]?\s*(\d+)\s*/\s*\d+\s*(?:mmhg)?',
            ],
            MetricType.BLOOD_PRESSURE_DIASTOLIC: [
                r'(?:bp|blood\s+pressure)\s*[:\-]?\s*\d+\s*/\s*(\d+)\s*(?:mmhg)?',
            ],
            MetricType.HEMOGLOBIN: [
                r'(?:hb|hemoglobin|haemoglobin)\s*[:\-]?\s*(\d+\.?\d*)\s*(g/dl|g/l)',
            ],
            MetricType.HBA1C: [
                r'(?:hba1c|hb\s*a1c|glycated\s+hemoglobin)\s*[:\-]?\s*(\d+\.?\d*)\s*(%)?',
            ],
        }
    
    def _init_unit_conversions(self):
        """Initialize unit conversion factors to standard units."""
        # Standard units: glucose (mg/dL), cholesterol (mg/dL), hemoglobin (g/dL), HbA1c (%)
        self.unit_conversions = {
            MetricType.GLUCOSE: {
                'mmol/l': 18.0,  # multiply by 18 to get mg/dL
                'mg/dl': 1.0,
            },
            MetricType.CHOLESTEROL_TOTAL: {
                'mmol/l': 38.67,  # multiply by 38.67 to get mg/dL
                'mg/dl': 1.0,
            },
            MetricType.CHOLESTEROL_LDL: {
                'mmol/l': 38.67,
                'mg/dl': 1.0,
            },
            MetricType.CHOLESTEROL_HDL: {
                'mmol/l': 38.67,
                'mg/dl': 1.0,
            },
            MetricType.TRIGLYCERIDES: {
                'mmol/l': 88.57,  # multiply by 88.57 to get mg/dL
                'mg/dl': 1.0,
            },
            MetricType.HEMOGLOBIN: {
                'g/l': 0.1,  # divide by 10 to get g/dL
                'g/dl': 1.0,
            },
        }
    
    def _init_section_patterns(self):
        """Initialize patterns for detecting different sections of medical reports."""
        self.section_patterns = {
            'lab_results': r'(?:lab(?:oratory)?\s+results?|test\s+results?|investigations?)',
            'doctor_notes': r'(?:doctor\'?s?\s+notes?|physician\'?s?\s+notes?|clinical\s+notes?|observations?)',
            'prescriptions': r'(?:prescriptions?|medications?|drugs?|rx)',
            'recommendations': r'(?:recommendations?|advice|suggestions?)',
        }
    
    def extract_structured_data(self, text: str, report_id: str = "unknown") -> StructuredHealthData:
        """
        Extract numeric health metrics from text.
        
        Args:
            text: Extracted text from medical report
            report_id: Unique identifier for the report
            
        Returns:
            StructuredHealthData: Parsed health metrics with units
            
        Raises:
            InsufficientDataError: If no metrics found
        """
        if not text or not text.strip():
            raise InsufficientDataError("Empty text provided for extraction")
        
        metrics = []
        text_lower = text.lower()
        
        # Extract metrics for each type
        for metric_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    try:
                        value_str = match.group(1)
                        value = float(value_str)
                        
                        # Extract unit if present
                        unit = match.group(2) if len(match.groups()) > 1 else None
                        if unit:
                            unit = unit.lower()
                        else:
                            unit = self._get_default_unit(metric_type)
                        
                        # Normalize to standard unit
                        normalized_value, standard_unit = self._normalize_unit(
                            metric_type, value, unit
                        )
                        
                        # Get context for confidence scoring
                        context = self._get_context(text, match.start(), match.end())
                        confidence = self._calculate_confidence(metric_type, context)
                        
                        metric = HealthMetric(
                            metric_type=metric_type,
                            value=normalized_value,
                            unit=standard_unit,
                            extracted_at=datetime.now(),
                            confidence=confidence
                        )
                        metrics.append(metric)
                        
                    except (ValueError, IndexError):
                        continue
        
        if not metrics:
            raise InsufficientDataError("No health metrics found in text")
        
        return StructuredHealthData(
            metrics=metrics,
            report_id=report_id,
            extraction_timestamp=datetime.now()
        )
    
    def extract_textual_notes(self, text: str) -> List[TextualNote]:
        """
        Extract doctor notes, prescriptions, and recommendations.
        
        This method identifies different sections in medical reports (doctor notes,
        prescriptions, recommendations) and preserves their context and relationships.
        Encrypted or redacted text is automatically excluded.
        
        Args:
            text: Extracted text from medical report
            
        Returns:
            List of TextualNote objects with section information and preserved context
        """
        notes = []
        
        # Split text into lines for processing
        lines = text.split('\n')
        current_section = 'general'
        current_content = []
        section_start_line = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                if current_content:
                    # Save accumulated content with context preservation
                    content = '\n'.join(current_content).strip()
                    if content and not self._is_encrypted_or_redacted(content):
                        notes.append(TextualNote(
                            content=content,
                            section=current_section,
                            page_number=None  # Can be enhanced with page tracking
                        ))
                    current_content = []
                continue
            
            # Check if line indicates a new section
            section_found = False
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower, re.IGNORECASE):
                    # Save previous section content
                    if current_content:
                        content = '\n'.join(current_content).strip()
                        if content and not self._is_encrypted_or_redacted(content):
                            notes.append(TextualNote(
                                content=content,
                                section=current_section,
                                page_number=None
                            ))
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_start_line = i
                    section_found = True
                    break
            
            if not section_found:
                # Add line to current section, preserving context
                current_content.append(line)
        
        # Save final section
        if current_content:
            content = '\n'.join(current_content).strip()
            if content and not self._is_encrypted_or_redacted(content):
                notes.append(TextualNote(
                    content=content,
                    section=current_section,
                    page_number=None
                ))
        
        return notes
    
    def identify_metric_type(self, value: float, context: str) -> Optional[MetricType]:
        """
        Identify metric type from value and surrounding context.
        
        Args:
            value: Numeric value of the metric
            context: Surrounding text context
            
        Returns:
            MetricType if identified, None if ambiguous
        """
        context_lower = context.lower()
        
        # Check each metric type pattern against context
        matches = []
        for metric_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, context_lower, re.IGNORECASE):
                    matches.append(metric_type)
                    break
        
        # Return single match, or None if ambiguous
        if len(matches) == 1:
            return matches[0]
        return None
    
    def extract_with_ambiguity_flagging(self, text: str, report_id: str = "unknown") -> ExtractionResult:
        """
        Extract data and flag ambiguous values for manual review.
        
        Args:
            text: Extracted text from medical report
            report_id: Unique identifier for the report
            
        Returns:
            ExtractionResult containing structured data, notes, and ambiguous values
        """
        # Extract structured data
        try:
            structured_data = self.extract_structured_data(text, report_id)
        except InsufficientDataError:
            structured_data = StructuredHealthData(
                metrics=[],
                report_id=report_id,
                extraction_timestamp=datetime.now()
            )
        
        # Extract textual notes
        textual_notes = self.extract_textual_notes(text)
        
        # Find ambiguous numeric values
        ambiguous_values = self._find_ambiguous_values(text)
        
        return ExtractionResult(
            structured_data=structured_data,
            textual_notes=textual_notes,
            ambiguous_values=ambiguous_values
        )
    
    def _normalize_unit(self, metric_type: MetricType, value: float, unit: str) -> Tuple[float, str]:
        """
        Convert metric value to standard unit.
        
        Args:
            metric_type: Type of health metric
            value: Original value
            unit: Original unit
            
        Returns:
            Tuple of (normalized_value, standard_unit)
        """
        if metric_type not in self.unit_conversions:
            return value, unit
        
        conversions = self.unit_conversions[metric_type]
        unit_lower = unit.lower() if unit else ''
        
        if unit_lower in conversions:
            conversion_factor = conversions[unit_lower]
            normalized_value = value * conversion_factor
            # Get standard unit (the one with factor 1.0)
            standard_unit = next(u for u, f in conversions.items() if f == 1.0)
            return normalized_value, standard_unit
        
        return value, unit
    
    def _get_default_unit(self, metric_type: MetricType) -> str:
        """Get default unit for a metric type."""
        defaults = {
            MetricType.GLUCOSE: 'mg/dl',
            MetricType.CHOLESTEROL_TOTAL: 'mg/dl',
            MetricType.CHOLESTEROL_LDL: 'mg/dl',
            MetricType.CHOLESTEROL_HDL: 'mg/dl',
            MetricType.TRIGLYCERIDES: 'mg/dl',
            MetricType.BMI: '',
            MetricType.BLOOD_PRESSURE_SYSTOLIC: 'mmhg',
            MetricType.BLOOD_PRESSURE_DIASTOLIC: 'mmhg',
            MetricType.HEMOGLOBIN: 'g/dl',
            MetricType.HBA1C: '%',
        }
        return defaults.get(metric_type, '')
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """
        Get surrounding context for a match.
        
        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            window: Number of characters to include on each side
            
        Returns:
            Context string
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _calculate_confidence(self, metric_type: MetricType, context: str) -> float:
        """
        Calculate confidence score based on context clarity.
        
        Args:
            metric_type: Type of metric
            context: Surrounding text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Start with base confidence
        confidence = 0.7
        
        # Increase confidence if metric name is clearly present
        metric_keywords = {
            MetricType.GLUCOSE: ['glucose', 'blood sugar', 'fasting'],
            MetricType.CHOLESTEROL_TOTAL: ['total cholesterol', 'cholesterol'],
            MetricType.CHOLESTEROL_LDL: ['ldl', 'low density'],
            MetricType.CHOLESTEROL_HDL: ['hdl', 'high density'],
            MetricType.TRIGLYCERIDES: ['triglycerides', 'tg'],
            MetricType.BMI: ['bmi', 'body mass index'],
            MetricType.BLOOD_PRESSURE_SYSTOLIC: ['blood pressure', 'bp'],
            MetricType.BLOOD_PRESSURE_DIASTOLIC: ['blood pressure', 'bp'],
            MetricType.HEMOGLOBIN: ['hemoglobin', 'haemoglobin', 'hb'],
            MetricType.HBA1C: ['hba1c', 'glycated'],
        }
        
        context_lower = context.lower()
        keywords = metric_keywords.get(metric_type, [])
        
        for keyword in keywords:
            if keyword in context_lower:
                confidence = min(1.0, confidence + 0.15)
                break
        
        # Decrease confidence if context is unclear
        if len(context.strip()) < 20:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _is_encrypted_or_redacted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted or redacted.
        
        This method detects various redaction patterns and encrypted content
        to ensure sensitive information is excluded from extraction.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears encrypted or redacted
        """
        # Check for common redaction patterns
        redaction_patterns = [
            r'\[redacted\]',
            r'\[REDACTED\]',
            r'\*\*\*+',
            r'xxx+',
            r'XXX+',
            r'####+',
            r'\[encrypted\]',
            r'\[ENCRYPTED\]',
            r'\[removed\]',
            r'\[REMOVED\]',
            r'\[censored\]',
            r'\[CENSORED\]',
            r'█+',  # Block character used for redaction
            r'▓+',  # Another block character
            r'\[\.\.\.+\]',  # Ellipsis in brackets
        ]
        
        text_lower = text.lower()
        for pattern in redaction_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        # Check for high ratio of non-alphanumeric characters (possible encryption)
        if len(text) > 20:
            alphanumeric = sum(c.isalnum() or c.isspace() for c in text)
            ratio = alphanumeric / len(text)
            if ratio < 0.5:
                return True
        
        # Check for base64-like patterns (long strings of alphanumeric without spaces)
        if len(text) > 50:
            # Look for long sequences without spaces
            words = text.split()
            for word in words:
                if len(word) > 40 and word.isalnum():
                    # Likely encrypted/encoded content
                    return True
        
        return False
    
    def _find_ambiguous_values(self, text: str) -> List[Dict[str, any]]:
        """
        Find numeric values that could match multiple metric types.
        
        Args:
            text: Full text to analyze
            
        Returns:
            List of dictionaries containing ambiguous value information
        """
        ambiguous = []
        
        # Find all numeric values with minimal context
        numeric_pattern = r'(\d+\.?\d*)'
        matches = re.finditer(numeric_pattern, text)
        
        for match in matches:
            value = float(match.group(1))
            context = self._get_context(text, match.start(), match.end(), window=30)
            
            # Check how many metric types could match this value
            possible_types = []
            for metric_type in MetricType:
                if self._could_be_metric_type(value, metric_type, context):
                    possible_types.append(metric_type)
            
            # Flag if multiple types possible
            if len(possible_types) > 1:
                ambiguous.append({
                    'value': value,
                    'context': context,
                    'possible_types': [mt.value for mt in possible_types],
                    'position': match.start()
                })
        
        return ambiguous
    
    def _could_be_metric_type(self, value: float, metric_type: MetricType, context: str) -> bool:
        """
        Check if a value could plausibly be a specific metric type.
        
        Args:
            value: Numeric value
            metric_type: Metric type to check
            context: Surrounding context
            
        Returns:
            True if value could be this metric type
        """
        # Check if any pattern for this metric type matches the context
        if metric_type in self.patterns:
            for pattern in self.patterns[metric_type]:
                if re.search(pattern, context, re.IGNORECASE):
                    return True
        
        # Check if value is in plausible range for metric type
        plausible_ranges = {
            MetricType.GLUCOSE: (50, 500),
            MetricType.CHOLESTEROL_TOTAL: (100, 400),
            MetricType.CHOLESTEROL_LDL: (50, 300),
            MetricType.CHOLESTEROL_HDL: (20, 100),
            MetricType.TRIGLYCERIDES: (50, 500),
            MetricType.BMI: (10, 60),
            MetricType.BLOOD_PRESSURE_SYSTOLIC: (70, 200),
            MetricType.BLOOD_PRESSURE_DIASTOLIC: (40, 130),
            MetricType.HEMOGLOBIN: (5, 20),
            MetricType.HBA1C: (4, 15),
        }
        
        if metric_type in plausible_ranges:
            min_val, max_val = plausible_ranges[metric_type]
            return min_val <= value <= max_val
        
        return False
