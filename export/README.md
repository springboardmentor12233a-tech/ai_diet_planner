# Report Exporter Module

The Report Exporter module provides functionality to export personalized diet plans in professional PDF and structured JSON formats.

## Features

### PDF Export
- **Professional Medical Report Template**: Clean, readable layout with proper typography
- **Comprehensive Sections**:
  - Patient Information (demographics, preferences, allergies)
  - Health Summary (detected conditions, dietary restrictions, recommendations)
  - Daily Diet Plan (detailed meal breakdown with portions and nutrition)
  - Nutritional Breakdown (macronutrient charts and daily totals)
- **Visual Elements**:
  - Macronutrient pie charts
  - Color-coded tables for easy reading
  - Professional styling with medical disclaimer
- **Performance**: Generates PDFs in under 5 seconds

### JSON Export
- **Structured Data Format**: Complete diet plan data in JSON
- **Schema Validation**: Built-in validation against defined schema
- **Comprehensive Data**: Includes all meals, portions, nutrients, restrictions, and recommendations
- **Performance**: Generates JSON in under 2 seconds
- **Integration Ready**: Easy to integrate with other systems and applications

## Installation

Required dependencies:
```bash
pip install reportlab PyPDF2
```

## Usage

### Basic PDF Export

```python
from ai_diet_planner.export import ReportExporter
from ai_diet_planner.models import DietPlan, PatientProfile

# Initialize exporter
exporter = ReportExporter()

# Export diet plan to PDF
pdf_bytes = exporter.export_pdf(diet_plan, patient_info=patient_profile)

# Save to file
with open("diet_plan_report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Basic JSON Export

```python
from ai_diet_planner.export import ReportExporter

# Initialize exporter
exporter = ReportExporter()

# Export diet plan to JSON
json_str = exporter.export_json(diet_plan)

# Validate schema
is_valid = exporter.validate_json_schema(json_str)

# Save to file
with open("diet_plan_data.json", "w") as f:
    f.write(json_str)
```

### Complete Example

See `example_usage.py` for a complete working example that demonstrates:
- Creating a sample diet plan with multiple meals
- Creating a patient profile
- Exporting to both PDF and JSON formats
- Validating JSON schema
- Saving output files

Run the example:
```bash
python ai_diet_planner/export/example_usage.py
```

## API Reference

### ReportExporter Class

#### `export_pdf(diet_plan: DietPlan, patient_info: Optional[PatientProfile] = None) -> bytes`

Generate a PDF report of the diet plan.

**Parameters:**
- `diet_plan` (DietPlan): The generated diet plan to export
- `patient_info` (PatientProfile, optional): Patient information for the header section

**Returns:**
- `bytes`: PDF file content as bytes

**Raises:**
- `ValueError`: If diet plan is None or contains no meals
- `RuntimeError`: If PDF generation fails

**Example:**
```python
pdf_bytes = exporter.export_pdf(diet_plan, patient_info=patient_profile)
```

#### `export_json(diet_plan: DietPlan) -> str`

Export diet plan as structured JSON.

**Parameters:**
- `diet_plan` (DietPlan): The generated diet plan to export

**Returns:**
- `str`: JSON string containing the complete diet plan

**Raises:**
- `ValueError`: If diet plan is None
- `RuntimeError`: If JSON generation fails

**Example:**
```python
json_str = exporter.export_json(diet_plan)
```

#### `validate_json_schema(json_data: str) -> bool`

Validate JSON against the defined schema.

**Parameters:**
- `json_data` (str): JSON string to validate

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
is_valid = exporter.validate_json_schema(json_str)
```

## JSON Schema

The exported JSON follows this structure:

```json
{
  "plan_id": "string",
  "patient_id": "string",
  "generated_date": "ISO8601 datetime",
  "health_summary": {
    "conditions": [
      {
        "type": "string",
        "confidence": "float",
        "detected_at": "ISO8601 datetime",
        "contributing_metrics": ["string"]
      }
    ],
    "restrictions": [
      {
        "type": "string",
        "items": ["string"],
        "severity": "string"
      }
    ],
    "recommendations": ["string"]
  },
  "diet_plan": {
    "daily_calories": "float",
    "macronutrient_targets": {
      "protein_percent": "float",
      "carbs_percent": "float",
      "fat_percent": "float"
    },
    "meals": [
      {
        "meal_type": "breakfast|lunch|snack|dinner",
        "total_calories": "float",
        "total_protein_g": "float",
        "total_carbs_g": "float",
        "total_fat_g": "float",
        "foods": [
          {
            "name": "string",
            "portion": "string",
            "amount": "float",
            "unit": "string",
            "calories": "float",
            "protein_g": "float",
            "carbs_g": "float",
            "fat_g": "float",
            "category": "string"
          }
        ]
      }
    ]
  }
}
```

## PDF Report Sections

### 1. Title
- "Personalized Diet Plan Report" header

### 2. Patient Information
- Patient ID
- Age, Gender
- Height, Weight
- Activity Level
- Dietary Style
- Allergies

### 3. Health Summary
- Detected Health Conditions (with confidence scores)
- Dietary Restrictions (with severity levels)
- Dietary Recommendations

### 4. Daily Diet Plan
- Target Daily Calories
- Macronutrient Targets (percentages)
- Meal Details:
  - Breakfast (25% of daily calories)
  - Lunch (35% of daily calories)
  - Snack (10% of daily calories)
  - Dinner (30% of daily calories)
- For each meal:
  - Food items with portions
  - Nutritional breakdown (calories, protein, carbs, fat)
  - Meal totals

### 5. Nutritional Breakdown
- Macronutrient Pie Chart
- Daily Totals Table
- Percentage breakdown

### 6. Footer
- Medical Disclaimer
- Generation Date and Plan ID

## Testing

Run the test suite:
```bash
python -m pytest ai_diet_planner/export/test_report_exporter.py -v
```

The test suite includes:
- **Unit Tests**: Specific scenarios and edge cases
- **Performance Tests**: Verify generation times meet requirements
- **Schema Validation Tests**: Ensure JSON structure is correct
- **Edge Case Tests**: Handle missing data gracefully

## Performance Requirements

- **PDF Generation**: Must complete within 5 seconds (Requirement 11.4)
- **JSON Generation**: Must complete within 2 seconds (Requirement 12.4)

Both requirements are validated in the test suite.

## Error Handling

The module provides clear error messages for common issues:

- **Invalid Input**: `ValueError` for None or empty diet plans
- **Generation Failures**: `RuntimeError` with descriptive error messages
- **Schema Validation**: Returns False for invalid JSON structure

## Design Principles

1. **Professional Output**: Medical-grade report formatting
2. **Comprehensive Data**: All relevant information included
3. **Performance**: Fast generation for good user experience
4. **Validation**: Built-in schema validation for data integrity
5. **Error Handling**: Clear error messages for debugging
6. **Extensibility**: Easy to add new sections or formats

## Requirements Validation

This module validates the following requirements:

- **Requirement 11.1**: PDF export with complete diet plan
- **Requirement 11.2**: PDF includes patient info, health summary, and meal plans
- **Requirement 11.3**: PDF formatted for readability
- **Requirement 11.4**: PDF generation within 5 seconds
- **Requirement 11.5**: Descriptive error messages
- **Requirement 12.1**: JSON export with structured data
- **Requirement 12.2**: JSON includes all diet plan data
- **Requirement 12.3**: JSON schema validation
- **Requirement 12.4**: JSON generation within 2 seconds

## Future Enhancements

Potential improvements for future versions:

1. **Multiple PDF Templates**: Different styles for different use cases
2. **Localization**: Support for multiple languages
3. **Custom Branding**: Allow customization of colors, logos, fonts
4. **Additional Formats**: Excel, CSV, HTML exports
5. **Email Integration**: Direct email delivery of reports
6. **Batch Export**: Export multiple diet plans at once
7. **Watermarking**: Add watermarks for draft reports
8. **Digital Signatures**: Support for signed medical reports

## License

Part of the AI NutriCare System.
