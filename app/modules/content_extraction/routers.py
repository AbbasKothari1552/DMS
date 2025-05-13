from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.db.session import get_db
from app.db.models import FileMetadata
from app.modules.content_extraction.services import ContentExtractor

router = APIRouter()

@router.post("/extract/{file_id}")
async def extract_content(
    file_id: int,
    db=Depends(get_db)
):
    """Endpoint to trigger content extraction"""
    extractor = ContentExtractor(db)
    try:
        file_meta = extractor.extract_and_store_content(file_id)
        return JSONResponse({
            "status": file_meta.extraction_status,
            "file_id": file_meta.file_id,
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )