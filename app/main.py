from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import SessionLocal, engine
from db.base import Base
from modules.file_upload.routes import router as upload_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

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