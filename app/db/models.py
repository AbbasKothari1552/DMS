from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import event
from sqlalchemy.orm.session import object_session
import uuid
import os

from app.core.config import BASE_PATH, UPLOAD_DIR, CONTENT_EXTRACTION_DIR

from app.core.logging_config import get_logger
logger = get_logger(__name__)

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
    category = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.now())
    modified_date = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    upload_status = Column(String)
    error_message = Column(String, nullable=True)

    # one-to-one relation wit `text_metadata`
    text_metadata = relationship(
        "TextMetaData", back_populates="file", uselist=False, cascade="all, delete", passive_deletes=True
    )
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
    file_id = Column(Integer, ForeignKey("file_metadata.id", ondelete="CASCADE"))
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
    chunk_metadata = relationship(
        "ChunkMetadata", back_populates="text", uselist=False, cascade="all, delete", passive_deletes=True
    )


class ChunkMetadata(Base):
    __tablename__ = "chunk_metadata"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_metadata.id", ondelete="CASCADE"))
    text_metadata_id = Column(Integer, ForeignKey("text_metadata.id", ondelete="CASCADE"))
    chunk_index = Column(Integer)
    chunk_text = Column(Text)

    # Vectore id
    vector_id = Column(Integer, nullable=True)

    created_date = Column(DateTime, default=datetime.now())
    modified_date = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # relation with `text_metadata` table
    text = relationship("TextMetaData", back_populates="chunk_metadata")
    # relation with `file_metadata` table
    file = relationship("FileMetadata")



# file deletion handler
@event.listens_for(FileMetadata, "before_delete")
def delete_associated_files(mapper, connection, target):
    try:
        logger.info(f"Deleting file: {target.filename}")

        # Construct full path directly
        if target.upload_path:
            original_path = os.path.join(BASE_PATH, target.upload_path)
            if os.path.exists(original_path):
                os.remove(original_path)
                logger.info(f"Deleted original file: {original_path}")
            else:
                logger.warning(f"Original file not found: {original_path}")

        # Try to delete extracted text file from TextMetaData.upload_path
        # You must fetch it manually because relationship won't be loaded
        session = object_session(target)
        if session:
            text_meta = session.query(TextMetaData).filter_by(file_id=target.id).first()
            if text_meta and text_meta.upload_path:
                extracted_path = os.path.join(BASE_PATH, text_meta.upload_path)
                if os.path.exists(extracted_path):
                    os.remove(extracted_path)
                    logger.info(f"Deleted extracted text file: {text_meta.text_filename}")
                else:
                    logger.warning(f"Extracted file not found: {extracted_path}")

    except Exception as e:
        logger.error(f"File deletion failed for FileMetadata id {target.id}: {str(e)}")


# Delete text file
@event.listens_for(TextMetaData, "before_delete")
def delete_text_file(mapper, connection, target):

    try:
        logger.info(f"Deleting text file: {target.text_filename}")

        # Construct full path directly
        if target.upload_path:
            original_path = os.path.join(BASE_PATH, target.upload_path)
            if os.path.exists(original_path):
                os.remove(original_path)
                logger.info(f"Deleted text file: {original_path}")
            else:
                logger.warning(f"Text file not found: {original_path}")

    except Exception as e:
        logger.error(f"Text File deletion failed for TextMetadata id {target.id}: {str(e)}")
