from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class FileMetadataBase(BaseModel):
    file_id: str
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    content_type: Optional[str]
    upload_path: str
    extracted_text_path: str
    extraction_status: str
    created_date: datetime
    modified_date: datetime
    upload_status: Optional[str]
    error_message: Optional[str]

    class Config:
        orm_mode = True

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: int

    class Config:
        orm_mode = True