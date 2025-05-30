from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from typing import Dict
import os
import time

# import pytesseract from tesseract_config.py to use configured path
from app.core.tesseract_config import pytesseract

from app.core.logging_config import get_logger
logger = get_logger(__name__)


def extract_pdf_text(input_path: str, output_path: str) -> Dict:
    """Extract text from PDF, with OCR fallback"""
    try:
        # First try regular extraction
        text = extract_text(input_path)
        
        # If little text found, try OCR
        if len(text.strip()) < 100:
            images = convert_from_path(input_path)
            text = ""
            logger.info("Extracting with OCR Tesseract...")
            start_time = time.perf_counter()
            
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            method = "pdfminer+ocr"

            total_time = time.perf_counter() - start_time
            logger.info(f"OCR processing time: {total_time:.2f} seconds")
        else:
            method = "pdfminer"
        
        # Save extracted text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        return {
            "method": method,
            "word_count": len(text.split())
        }
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")