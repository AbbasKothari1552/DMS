import os

from dotenv import load_dotenv
load_dotenv()

DEBUG: bool = True
LOG_LEVEL: str = "error"

UPLOAD_DIR = os.getenv("UPLOAD_DIR")

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR")

CONTENT_EXTRACTION_DIR = os.getenv("CONTENT_EXTRACTION_DIR")
