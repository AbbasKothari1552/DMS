from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.init_db import init_db
from app.modules.file_upload.routes import router as upload_router
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    logger.info("Application starting up...")
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

# Include routers
app.include_router(upload_router, prefix="/api/files", tags=["files"])

@app.get("/")
def read_root():
    return {"message": "File Upload Service"}