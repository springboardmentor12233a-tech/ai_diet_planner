# OCR Module

Unified OCR engine for extracting text from medical reports in various formats.

## Overview

The OCR module provides a single, unified interface for extracting text from both images and PDF documents. It supports multiple OCR backends (Tesseract, EasyOCR) and includes a comprehensive image preprocessing pipeline to improve accuracy.

## Features

- **Multiple Backend Support**: Tesseract (default) and EasyOCR
- **Image Preprocessing Pipeline**:
  - Grayscale conversion
  - Noise reduction (Gaussian blur)
  - Contrast enhancement (CLAHE)
  - Binarization (Otsu's method)
  - Deskewing (Hough transform)
- **Confidence Scoring**: Each extraction includes confidence scores
- **Quality Validation**: Automatic quality check with 60% minimum confidence threshold
- **Multi-page PDF Support**: Preserves page order and provides per-page confidence scores

## Usage

### Basic Usage

```python
from ocr import OCREngine, UnreadableDocumentError

# Initialize engine with Tesseract backend (default)
engine = OCREngine(backend="tesseract")

# Extract text from an image
try:
    result = engine.extract_text_from_image("path/to/image.png")
    print(f"Confidence: {result.average_confidence:.2%}")
    print(f"Text: {result.full_text}")
except UnreadableDocumentError as e:
    print(f"Quality insufficient: {e}")

# Extract text from a PDF
try:
    result = engine.extract_text_from_pdf("path/to/document.pdf")
    print(f"Pages: {result.total_pages}")
    print(f"Average Confidence: {result.average_confidence:.2%}")
    
    # Access individual pages
    for page in result.pages:
        print(f"Page {page.page_number}: {page.confidence:.2%}")
except UnreadableDocumentError as e:
    print(f"Quality insufficient: {e}")
```

### Using EasyOCR Backend

```python
# Initialize with EasyOCR backend
engine = OCREngine(backend="easyocr")

result = engine.extract_text_from_image("path/to/image.png")
```

### Working with PIL Images

```python
from PIL import Image

# Load image
img = Image.open("path/to/image.png")

# Extract text from PIL Image object
result = engine.extract_text_from_image_obj(img, page_number=1)
```

## Data Structures

### OCRResult

Container for complete OCR results:

```python
@dataclass
class OCRResult:
    pages: List[ExtractedText]
    average_confidence: float
    total_pages: int
    backend_used: str
    
    @property
    def full_text(self) -> str:
        """Concatenated text from all pages"""
    
    @property
    def passes_quality_check(self) -> bool:
        """True if confidence >= 60%"""
```

### ExtractedText

Container for single page extraction:

```python
@dataclass
class ExtractedText:
    text: str
    confidence: float
    page_number: Optional[int]
    extraction_timestamp: datetime
```

## Quality Validation

The OCR engine automatically validates extraction quality:

- **Minimum Confidence**: 60% (0.60)
- **Behavior**: Raises `UnreadableDocumentError` if quality is insufficient
- **Per-page Scoring**: Each page gets individual confidence score
- **Average Scoring**: Overall result uses average of all page confidences

## Image Preprocessing

The preprocessing pipeline improves OCR accuracy:

1. **Grayscale Conversion**: Reduces complexity
2. **Noise Reduction**: Gaussian blur removes artifacts
3. **Contrast Enhancement**: CLAHE improves text visibility
4. **Binarization**: Otsu's method creates clean black/white image
5. **Deskewing**: Hough transform corrects rotation

## Configuration

### PDF Processing

- **DPI**: 300 (configurable via `OCREngine.PDF_DPI`)
- **Page Processing**: Parallel processing with order preservation

### Confidence Threshold

- **Minimum**: 60% (configurable via `OCREngine.MINIMUM_CONFIDENCE`)

## Testing

The module includes comprehensive tests:

```bash
# Run unit tests
python -m pytest ocr/test_ocr_engine.py -v

# Run integration tests with real files
python -m pytest ocr/test_ocr_integration.py -v

# Run all tests
python -m pytest ocr/ -v
```

## Example Script

Run the example script to see the OCR engine in action:

```bash
python -m ocr.example_usage
```

## Requirements

- `pytesseract>=0.3.13`
- `pdf2image>=1.16.3`
- `Pillow>=12.1.0`
- `opencv-python>=4.12.0`
- `numpy>=2.2.6`
- `easyocr` (optional, for EasyOCR backend)

## Migration from Old Code

The old `ocr_images.py` and `ocr_pdf.py` files have been replaced by the unified `ocr_engine.py`. 

### Old Code

```python
# ocr_images.py
from PIL import Image
import pytesseract as tess

img = Image.open("image.png")
text = tess.image_to_string(img)
```

### New Code

```python
from ocr import OCREngine

engine = OCREngine()
result = engine.extract_text_from_image("image.png")
text = result.full_text
confidence = result.average_confidence
```

## Design Requirements

This implementation satisfies the following requirements from the design document:

- **Requirement 2.1**: OCR extraction from PDF documents with 90%+ accuracy
- **Requirement 2.2**: OCR extraction from image documents with 90%+ accuracy
- **Requirement 2.3**: Error handling for unreadable documents
- **Requirement 2.5**: Page order preservation in multi-page documents

## Architecture

The OCR engine follows these design principles:

- **Configurable Backend**: Easy to switch between Tesseract and EasyOCR
- **Preprocessing Pipeline**: Improves accuracy through systematic image enhancement
- **Quality Validation**: Ensures only high-quality extractions are accepted
- **Metadata Tracking**: Preserves confidence scores and timestamps
- **Error Handling**: Clear error messages for quality issues
