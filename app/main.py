from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Setup admin
setup_admin(app)

# Include routers
app.include_router(upload_router, prefix="/api/files", tags=["files"])
app.include_router(semantic_search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


# Mount document folder as /uploads
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR), 
    name="uploads"
)
# Not working --debug-- 

@app.get("/")
def read_root():
    return {"message": "File Upload Service"}