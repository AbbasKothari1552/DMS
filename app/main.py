from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# admin app integration
from sqladmin import Admin
import os

from app.admin.admin_init import setup_admin
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.init_db import init_db
from app.core.config import UPLOAD_DIR

# add routes
from app.routes.file_upload_routes import router as upload_router
from app.routes.semantic_search_routes import router as semantic_search_router
from app.routes.chat_routes import router as chat_router
from app.modules.embeddings.embedder import Embedder

from app.core.logging_config import get_logger
logger = get_logger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Setup Jinja2 template rendering
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    logger.info("Application starting up...")
    # Warm up the embedding model
    # Embedder()  # This triggers the model load
    logger.info("Embedding model warmed up and ready")
    # initialize database
    init_db()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutting down...")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup admin
setup_admin(app)

# Include routers
app.include_router(upload_router, prefix="/api/files", tags=["files"])
app.include_router(semantic_search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

# Get the absolute path to the 'documents' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")

app.mount("/uploads", StaticFiles(directory=DOCUMENTS_DIR), name="uploads")

# # Mount document folder as /uploads
# app.mount(
#     "/uploads",
#     StaticFiles(directory="documents"), 
#     name="uploads"
# )

# upload files html page
@app.get("/upload", response_class=HTMLResponse)
def read_root(request: Request):
    print("Templates:", templates)
    return templates.TemplateResponse("upload_files.html", {"request": request})

# semantic search html page
@app.get("/chat", response_class=HTMLResponse)
def semantic_search(request: Request):
    print("Templates:", templates)
    return templates.TemplateResponse("semantic_search.html", {"request": request})

# Rag chat html page
@app.get("/rag_chat", response_class=HTMLResponse)
def rag_chat(request: Request):
    print("Templates:", templates)
    return templates.TemplateResponse("rag_chat.html", {"request": request})
