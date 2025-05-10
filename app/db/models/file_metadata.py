from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from db.base import Base
import uuid
import os

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, index=True)
    file_type = Column(String)
    file_size = Column(Integer)
    content_type = Column(String)
    upload_path = Column(String)
    created_date = Column(DateTime, default=datetime.now())
    modified_date = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    upload_status = Column(String)
    error_message = Column(String, nullable=True)


    @property
    def full_path(self):
        from app.core.config import UPLOAD_DIR
        return os.path.join(UPLOAD_DIR, self.upload_path)