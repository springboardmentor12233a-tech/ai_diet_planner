import re
from typing import Dict, List, Tuple
from app.utils.pdf_parser import pdf_parser
from app.services.ocr_service import ocr_service
from app.services.encryption import encryption_service
from app.utils.data_validation import validator
import json

class DataExtractionService:
    # Common medical test patterns
    MEDICAL_PATTERNS = {
        "blood_sugar": [
            r"fasting\s+(?:blood\s+)?(?:glucose|sugar)\s*\(?fbs\)?[:\s]*(\d+\.?\d*)",
            r"(?:blood\s+)?(?:glucose|sugar)\s*(?:level|test)?[:\s]*(\d+\.?\d*)",
            r"fbs[:\s]*(\d+\.?\d*)",
            r"fasting\s+(?:blood\s+)?(?:glucose|sugar)[:\s]*(\d+\.?\d*)",
            r"hba1c[:\s]*(\d+\.?\d*)",
            r"glucose[:\s]*(\d+\.?\d*)",
        ],
        "cholesterol": [
            r"(?:total\s+)?cholesterol[:\s]*(\d+\.?\d*)\s*(?:mg/dl)?",
            r"total\s+chol[:\s]*(\d+\.?\d*)",
        ],
        "hdl": [
            r"hdl\s+cholesterol[:\s]*(\d+\.?\d*)",
            r"hdl[:\s]*(\d+\.?\d*)",
        ],
        "ldl": [
            r"ldl\s+cholesterol[:\s]*(\d+\.?\d*)",
            r"ldl[:\s]*(\d+\.?\d*)",
        ],
        "triglycerides": [
            r"triglycerides?[:\s]*(\d+\.?\d*)",
            r"trig[:\s]*(\d+\.?\d*)",
        ],
        "bmi": [
            r"bmi[:\s]*(\d+\.?\d*)",
            r"body\s+mass\s+index[:\s]*(\d+\.?\d*)",
        ],
        "blood_pressure": [
            r"blood\s+pressure[:\s]*(\d+)\s*/\s*(\d+)",
            r"bp[:\s]*(\d+)\s*/\s*(\d+)",
            r"(\d+)\s*/\s*(\d+)\s*mmhg",
        ],
        "hemoglobin": [
            r"hemoglobin\s*\(hb\)[:\s]*(\d+\.?\d*)",
            r"hb[:\s]*(\d+\.?\d*)",
            r"hemoglobin[:\s]*(\d+\.?\d*)",
        ],
        "vitamin_d": [
            r"vitamin\s+d[:\s]*(\d+\.?\d*)",
            r"25-oh\s+vitamin\s+d[:\s]*(\d+\.?\d*)",
        ],
        "iron": [
            r"serum\s+iron[:\s]*(\d+\.?\d*)",
            r"iron\s+level[:\s]*(\d+\.?\d*)",
        ]
    }
    
    def __init__(self):
        self.compiled_patterns = {
            key: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for key, patterns in self.MEDICAL_PATTERNS.items()
        }
    
    def extract_from_file(self, file_path: str, file_type: str) -> Dict:
        """Main extraction method"""
        text = ""
        
        try:
            if file_type.lower() == "pdf":
                text = pdf_parser.extract_text(file_path)
            elif file_type.lower() in ["jpg", "jpeg", "png", "bmp"]:
                text = ocr_service.extract_text(image_path=file_path)
            elif file_type.lower() == "txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise ValueError(f"Failed to extract text from file: {str(e)}")
        
        if not text or len(text.strip()) < 10:
            raise ValueError("Insufficient text extracted from document")
        
        return self.extract_structured_data(text)
    
    def extract_numeric_data(self, text: str) -> Dict:
        """Extract numeric health metrics"""
        numeric_data = {}
        
        for metric, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    if metric == "blood_pressure":
                        # Handle systolic/diastolic
                        if isinstance(matches[0], tuple):
                            numeric_data["systolic_bp"] = float(matches[0][0])
                            numeric_data["diastolic_bp"] = float(matches[0][1])
                        else:
                            # Try to find both values
                            bp_pattern = r"(\d+)\s*/\s*(\d+)"
                            bp_match = re.search(bp_pattern, text, re.IGNORECASE)
                            if bp_match:
                                numeric_data["systolic_bp"] = float(bp_match.group(1))
                                numeric_data["diastolic_bp"] = float(bp_match.group(2))
                    else:
                        # Take the first match
                        value = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        try:
                            numeric_data[metric] = float(value)
                        except (ValueError, TypeError):
                            continue
                    break  # Found a match, move to next metric
        
        # Clean and validate
        numeric_data = validator.clean_numeric_data(numeric_data)
        return numeric_data
    
    def extract_textual_data(self, text: str) -> Dict:
        """Extract doctor notes and prescriptions"""
        # Look for prescription sections
        prescription_patterns = [
            r"prescription[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
            r"medication[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
            r"doctor['\s]?s\s+notes?[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
            r"comments?[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
            r"notes?[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
        ]
        
        prescriptions = []
        notes = []
        
        for pattern in prescription_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                if "prescription" in pattern.lower() or "medication" in pattern.lower():
                    prescriptions.extend(matches)
                else:
                    notes.extend(matches)
        
        # If no specific sections found, extract sentences with medical keywords
        if not prescriptions and not notes:
            medical_keywords = [
                r".*?(?:diabetes|diabetic|sugar|glucose|cholesterol|blood pressure|bp|bmi|weight|diet|exercise|medication|prescribe|recommend).*?[.!?]",
            ]
            for keyword_pattern in medical_keywords:
                matches = re.findall(keyword_pattern, text, re.IGNORECASE)
                notes.extend(matches[:5])  # Limit to first 5 matches
        
        return {
            "prescriptions": "\n".join(prescriptions) if prescriptions else "",
            "doctor_notes": "\n".join(notes) if notes else text[:2000]  # Fallback to first 2000 chars
        }
    
    def extract_structured_data(self, text: str) -> Dict:
        """Combine numeric and textual extraction"""
        numeric_data = self.extract_numeric_data(text)
        textual_data = self.extract_textual_data(text)
        
        return {
            "numeric_data": numeric_data,
            "textual_data": textual_data,
            "raw_text": text[:5000]  # Store first 5000 chars for reference
        }
    
    def save_extracted_data(self, report_id: int, extracted_data: Dict, db):
        """Save extracted data to database (encrypted)"""
        from app.models.database import MedicalReport
        from datetime import datetime
        
        report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
        if report:
            # Encrypt sensitive data
            report.encrypted_data = encryption_service.encrypt(extracted_data["raw_text"])
            report.numeric_data = extracted_data["numeric_data"]  # JSON field
            report.textual_data = encryption_service.encrypt(
                json.dumps(extracted_data["textual_data"])
            )
            report.extraction_status = "completed"
            report.processed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(report)
            return report
        return None

data_extraction_service = DataExtractionService()
