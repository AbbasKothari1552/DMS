from sqladmin import ModelView
from app.db.models import FileMetadata, TextMetaData, ChunkMetadata

class FileMetadataAdmin(ModelView, model=FileMetadata):

    column_list = [FileMetadata.id, FileMetadata.file_id, FileMetadata.filename, FileMetadata.file_type, FileMetadata.file_size, FileMetadata.content_type, FileMetadata.upload_path, FileMetadata.created_date, FileMetadata.modified_date]
    name = "File Metadata"
    name_plural = "Files Metadata"

class TextMetadataAdmin(ModelView, model=TextMetaData):
    
    column_list = [TextMetaData.id, TextMetaData.file_id, TextMetaData.text_filename, TextMetaData.upload_path, TextMetaData.file_size, TextMetaData.extraction_status, TextMetaData.created_date, TextMetaData.modified_date]
    name = "Text Metadata"
    name_plural = "Texts Metadata"

class ChunkMetadataAdmin(ModelView, model=ChunkMetadata):

    column_list = [ChunkMetadata.id, ChunkMetadata.text_metadata_id, ChunkMetadata.file_id, ChunkMetadata.chunk_index, ChunkMetadata.chunk_text, ChunkMetadata.vector_id, ChunkMetadata.created_date, ChunkMetadata.modified_date]
    name = "Chunk Metadata"
    name_plural = "Chunks Metadata"
    