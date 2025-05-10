from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import FileMetadata

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # You can add initial data here if needed
    db = SessionLocal()
    try:
        # Example initialization
        pass
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized")