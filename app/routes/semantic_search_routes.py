from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.search.services import SemanticSearchService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/search")
def search_form(request: Request):
    return templates.TemplateResponse("semantic_search.html", {"request": request})

@router.post("/search")
def process_search(
    request: Request, 
    query: str = Form(...), 
    db: Session = Depends(get_db)
):
    service = SemanticSearchService(db)
    results = service.semantic_search(query)
    return templates.TemplateResponse("semantic_search.html", {"request": request, "results": results, "query": query})
