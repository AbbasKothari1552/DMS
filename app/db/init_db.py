from app.db.session import engine
from app.db.base import Base
from app.db.models import FileMetadata, TextMetaData  # models registeration

def init_db():
    Base.metadata.create_all(bind=engine)
