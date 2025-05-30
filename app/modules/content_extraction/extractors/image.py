from PIL import Image
from typing import Dict
from pathlib import Path
import time

# import pytesseract from tesseract_config.py to use configured path
from app.core.tesseract_config import pytesseract

from app.core.logging_config import get_logger
logger = get_logger(__name__)

def extract_image_text(input_path: str, output_path: str) -> Dict:
    """Extract text from image using OCR"""
    try:
        start_time = time.perf_counter()

        text = pytesseract.image_to_string(Image.open(input_path), lang="eng+hin+guj+ara", config="--psm 6")

        total_time = time.perf_counter() - start_time
        logger.info(f"OCR processing time: {total_time:.2f} seconds")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        return {
            "content_type": "ocr_text",
            "method": "tesseract",
            "word_count": len(text.split())
        }
    except Exception as e:
        raise Exception(f"OCR failed: {str(e)}")