# Data Extraction Module

This module provides functionality for extracting structured health metrics and textual notes from medical report text.

## Overview

The `DataExtractor` class uses regex patterns and context analysis to:
- Extract numeric health metrics (glucose, cholesterol, BMI, blood pressure, etc.)
- Normalize units to standard measurements
- Identify and extract textual notes (doctor notes, prescriptions, recommendations)
- Detect different sections of medical reports
- Flag ambiguous values for manual review

## Features

### Supported Health Metrics

The DataExtractor can identify and extract the following health metrics:

- **Glucose** (mg/dL, mmol/L)
- **Total Cholesterol** (mg/dL, mmol/L)
- **LDL Cholesterol** (mg/dL, mmol/L)
- **HDL Cholesterol** (mg/dL, mmol/L)
- **Triglycerides** (mg/dL, mmol/L)
- **BMI** (Body Mass Index)
- **Blood Pressure** - Systolic and Diastolic (mmHg)
- **Hemoglobin** (g/dL, g/L)
- **HbA1c** (%)

### Unit Normalization

All metrics are automatically converted to standard units:
- Glucose: mg/dL
- Cholesterol (all types): mg/dL
- Triglycerides: mg/dL
- Hemoglobin: g/dL
- Blood Pressure: mmHg
- HbA1c: %

### Section Detection

The extractor can identify and separate different sections of medical reports:
- Laboratory Results
- Doctor's Notes
- Prescriptions
- Recommendations

### Ambiguity Flagging

Values that could match multiple metric types are flagged for manual review, ensuring data accuracy.

## Usage

### Basic Usage

```python
from ai_diet_planner.extraction.data_extractor import DataExtractor

# Create an instance
extractor = DataExtractor()

# Extract structured health metrics
medical_text = """
Glucose: 120 mg/dL
Total Cholesterol: 200 mg/dL
Blood Pressure: 130/85 mmHg
"""

structured_data = extractor.extract_structured_data(medical_text, report_id="REPORT-001")

# Access extracted metrics
for metric in structured_data.metrics:
    print(f"{metric.metric_type.value}: {metric.value} {metric.unit}")
```

### Extracting Textual Notes

```python
# Extract textual notes
notes = extractor.extract_textual_notes(medical_text)

for note in notes:
    print(f"Section: {note.section}")
    print(f"Content: {note.content}")
```

### Complete Extraction with Ambiguity Flagging

```python
# Extract everything with ambiguity detection
result = extractor.extract_with_ambiguity_flagging(medical_text, report_id="REPORT-001")

print(f"Metrics extracted: {len(result.structured_data.metrics)}")
print(f"Notes extracted: {len(result.textual_notes)}")
print(f"Ambiguous values: {len(result.ambiguous_values)}")
```

## Requirements

This module validates the following requirements from the AI NutriCare System specification:

- **Requirement 3.1**: Extract all numeric health metrics from text
- **Requirement 3.2**: Associate metrics with correct type and unit
- **Requirement 3.3**: Flag ambiguous values for manual review
- **Requirement 3.4**: Output structured data in JSON-compatible format
- **Requirement 3.5**: Handle insufficient data gracefully

## Testing

Run the test suite:

```bash
pytest ai_diet_planner/extraction/test_data_extractor.py -v
```

Run the example:

```bash
python ai_diet_planner/extraction/example_usage.py
```

## Implementation Details

### Regex Patterns

The extractor uses carefully crafted regex patterns that:
- Are case-insensitive
- Handle various separators (colon, dash, space)
- Support optional parenthetical text (e.g., "Glucose (Fasting)")
- Match both with and without units

### Confidence Scoring

Each extracted metric includes a confidence score (0.0 to 1.0) based on:
- Clarity of metric name in context
- Presence of expected keywords
- Amount of surrounding context

### Context Analysis

The extractor examines surrounding text to:
- Disambiguate metric types
- Improve extraction accuracy
- Calculate confidence scores

## Error Handling

The module includes robust error handling:

- `InsufficientDataError`: Raised when no metrics can be extracted
- Malformed data is gracefully skipped
- Encrypted or redacted text is automatically excluded

## Future Enhancements

Potential improvements for future versions:
- Support for additional metric types
- Machine learning-based metric identification
- Multi-language support
- Enhanced ambiguity resolution
- Integration with medical ontologies (SNOMED CT, LOINC)
