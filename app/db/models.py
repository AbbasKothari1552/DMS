from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import uuid
import os


from app.db.base import Base

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

    # one-to-one relation wit `text_metadata`
    text_metadata = relationship("TextMetaData", back_populates="file", uselist=False)


    @property
    def full_path(self):
        from core.config import UPLOAD_DIR
        return os.path.join(UPLOAD_DIR, self.upload_path)
    
    @property
    def extracted_text_full_path(self):
        from core.config import CONTENT_EXTRACTION_DIR
        if self.extracted_text_path:
            return os.path.join(CONTENT_EXTRACTION_DIR, self.extracted_text_path)
        return None
    
class TextMetaData(Base):
    __tablename__ = "text_metadata"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_metadata.id"))
    # extracted text from file details
    text_filename = Column(String, index=True)
    upload_path = Column(String)
    file_size = Column(Integer)

    extraction_status = Column(String(20), default="pending")  # pending, completed, failed
    created_date = Column(DateTime, default=datetime.now())
    modified_date = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    error_message = Column(String, nullable=True)

    file = relationship("FileMetadata", back_populates="text_metadata")



