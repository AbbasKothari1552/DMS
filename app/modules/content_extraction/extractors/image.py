from PIL import Image
from typing import Dict
from pathlib import Path

# import pytesseract from tesseract_config.py to use configured path
from app.core.tesseract_config import pytesseract

def extract_image_text(input_path: str, output_path: str) -> Dict:
    """Extract text from image using OCR"""
    try:
        text = pytesseract.image_to_string(Image.open(input_path))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        return {
            "content_type": "ocr_text",
            "method": "tesseract",
            "word_count": len(text.split())
        }
    except Exception as e:
        raise Exception(f"OCR failed: {str(e)}")