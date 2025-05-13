from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
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
    # # connection with chunk_metadata` table
    # chunks = relationship("ChunkMetadata", secondary="text_metadata", viewonly=True)


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
    # one-to-one relation wit `text_metadata`
    chunk_metadata = relationship("ChunkMetadata", back_populates="text", uselist=False)


class ChunkMetadata(Base):
    __tablename__ = "chunk_metadata"

    id = Column(Integer, primary_key=True, index=True)
    text_metadata_id = Column(Integer, ForeignKey("text_metadata.id"))
    chunk_index = Column(Integer)
    chunk_text = Column(Text)

    # Vectore id
    vector_id = Column(Integer, nullable=True)

    created_date = Column(DateTime, default=datetime.now())
    modified_date = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # relation with `text_metadata` table
    text = relationship("TextMetaData", back_populates="chunk_metadata")




