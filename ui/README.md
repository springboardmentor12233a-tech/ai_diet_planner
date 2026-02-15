# AI NutriCare System - User Interface

This module provides a Streamlit-based web interface for the AI NutriCare System with full backend integration.

## Features

### Multi-Page Navigation
- **Upload**: Upload medical reports with real backend processing
- **Review**: Review extracted health data and alerts
- **Diet Plan**: View personalized diet recommendations
- **History**: Access past reports and diet plans

### Upload Page (Task 14.2 - Completed)
✓ **File Upload Component**: Drag-and-drop interface with format validation
✓ **Progress Tracking**: Real-time progress bar during processing
✓ **Backend Integration**: Full integration with AINutriCareOrchestrator
✓ **Patient Information**: Optional patient profile input (age, gender, height, weight, activity level)
✓ **Dietary Preferences**: Optional dietary style, allergies, and dislikes
✓ **Error Handling**: Clear error messages with troubleshooting steps
✓ **Success Confirmation**: Processing time and summary metrics display

### Session State Management
The application maintains state across pages using Streamlit's session state:
- Uploaded file information
- Report processing status
- Extracted health data (metrics and textual notes)
- Health conditions and alerts
- Diet rules and generated diet plans
- PDF and JSON exports
- Patient profile information

## Running the Application

### Prerequisites
Install required dependencies:
```bash
pip install -r requirements.txt
```

### Start the Application
From the project root directory:
```bash
streamlit run ai_diet_planner/ui/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage

### 1. Upload a Medical Report
- Navigate to the Upload page
- Drag and drop or select a medical report file
- **Supported formats**: PDF, JPEG, PNG, TIFF, TXT
- **Maximum file size**: 10 MB
- **Optional**: Enter patient information (age, gender, height, weight, activity level)
- **Optional**: Set dietary preferences (style, allergies, dislikes)
- Click "Process Report" to begin analysis
- Watch the progress bar as the system:
  - Validates the file
  - Extracts text (OCR for images/PDFs)
  - Analyzes health metrics (ML)
  - Interprets doctor notes (NLP)
  - Generates personalized diet plan
- View processing summary with metrics count, conditions detected, and alerts

### 2. Review Health Data
- Navigate to the Review page after upload
- View extracted health metrics
- Check health alerts and abnormal values
- Verify data accuracy

### 3. View Diet Plan
- Navigate to the Diet Plan page
- Review personalized meal recommendations
- View nutritional breakdowns
- Export as PDF or JSON

### 4. Access History
- Navigate to the History page
- View past medical reports
- Access previous diet plans
- Track health progress over time

## Architecture

### Session State Variables
- `current_page`: Active page name
- `uploaded_file`: Uploaded file object
- `report_id`: Unique report identifier
- `processing_status`: Current processing status
- `extracted_data`: Extracted health metrics (StructuredHealthData)
- `textual_notes`: Extracted doctor notes (List[TextualNote])
- `health_conditions`: Detected health conditions (List[HealthCondition])
- `health_alerts`: Generated alerts (List[Alert])
- `diet_rules`: Extracted dietary rules (List[DietRule])
- `diet_plan`: Generated diet plan (DietPlan)
- `pdf_export`: PDF export bytes
- `json_export`: JSON export string
- `processing_time`: Processing duration in seconds
- `patient_id`: Patient identifier
- `patient_profile`: Patient information

### Backend Integration Flow
1. **File Validation**: Check format and size
2. **Orchestrator Initialization**: Create AINutriCareOrchestrator instance
3. **File Preparation**: Convert Streamlit UploadedFile to processor UploadedFile
4. **Patient Profile**: Create PatientProfile and UserPreferences from form inputs
5. **Pipeline Processing**: 
   - Text extraction (OCR for images/PDFs)
   - Data extraction (metrics and notes)
   - ML health analysis (conditions and alerts)
   - NLP interpretation (diet rules)
   - Diet plan generation
   - PDF/JSON export
   - Database storage
6. **Result Display**: Show summary and store in session state

### Page Functions
- `render_upload_page()`: File upload with backend integration
- `render_review_page()`: Health data review
- `render_diet_plan_page()`: Diet plan display
- `render_history_page()`: Historical data view

## Requirements Validation

This module validates the following requirements:
- **13.1**: ✓ User Interface with drag-and-drop file upload component
- **13.2**: ✓ Display upload progress and status
- **13.3**: ✓ Display confirmation message and processing status
- **13.4**: ✓ Display clear error messages with resolution steps
- **13.5**: ✓ Display supported file formats and size limits

## Testing

### Run All UI Tests
```bash
# All UI tests
python -m pytest ai_diet_planner/ui/ -v

# Unit tests only
python -m pytest ai_diet_planner/ui/test_app.py -v

# Integration tests only
python -m pytest ai_diet_planner/ui/test_upload_integration.py -v
```

### Example Usage
```bash
# Run example demonstrations
python ai_diet_planner/ui/example_upload_usage.py
```

## Error Handling

### File Validation Errors
- **File too large**: "❌ File size exceeds 10 MB limit. Please upload a smaller file."
- **Unsupported format**: File uploader only accepts specified formats

### Processing Errors
- **OCR failure**: "Failed to extract text from report"
- **No metrics found**: "Could not extract health metrics"
- **System error**: Displays error with troubleshooting steps:
  1. Ensure the document is clear and readable
  2. Try uploading a higher quality scan
  3. Verify the file format is supported
  4. Check that the document contains health metrics

## Performance

### Processing Times (from requirements)
- Single-page report: < 30 seconds
- Multi-page report: < 60 seconds
- Diet plan generation: < 10 seconds
- PDF export: < 5 seconds
- JSON export: < 2 seconds

## Future Enhancements

### Planned for Remaining Tasks
- **Task 14.3**: Enhanced Review page with data visualization
- **Task 14.4**: Enhanced Diet Plan page with charts and export
- **Task 14.5**: History page with filtering and sorting
- **Task 14.6**: Property-based tests for UI components
- **Task 14.7**: Additional unit tests for UI rendering

### Additional Features
- Multi-file upload support
- Real-time OCR preview
- Interactive data correction
- Batch processing
- Mobile-responsive design
- Accessibility improvements (WCAG 2.1 AA)
- Multi-language support
- Dark mode theme

## Files

- `app.py`: Main Streamlit application with all pages
- `test_app.py`: Unit tests for UI components
- `test_upload_integration.py`: Integration tests for Upload page
- `example_upload_usage.py`: Example usage demonstrations
- `README.md`: This documentation
- `IMPLEMENTATION_SUMMARY.md`: Implementation details
