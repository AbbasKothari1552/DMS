import os

from dotenv import load_dotenv
load_dotenv()

DEBUG: bool = True
LOG_LEVEL: str = "error"

BASE_PATH = os.getenv("BASE_PATH")

UPLOAD_DIR = os.getenv("UPLOAD_DIR")

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

DATABASE_URL = os.getenv("DATABASE_URL")

VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR")

CONTENT_EXTRACTION_DIR = os.getenv("CONTENT_EXTRACTION_DIR")

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")

FAISS_METADATA_PATH = os.getenv("FAISS_METADATA_PATH")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

EMBEDDING_DIM = os.getenv("EMBEDDING_DIM")

LLM_MODEL = os.getenv("LLM_MODEL")
