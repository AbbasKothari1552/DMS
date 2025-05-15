from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.rag_chat.services import RAGQAService

from app.core.logging_config import get_logger
logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/chat")
def chat_form(request: Request):
    return templates.TemplateResponse("rag_chat.html", {"request": request})


@router.post("/chat")
def chat_answer(
    request: Request,
    query: str = Form(...),
    db: Session = Depends(get_db)
):
    qa_service = RAGQAService(db)
    result = qa_service.answer_query(query)

    return templates.TemplateResponse("rag_chat.html", {
        "request": request,
        "query": query,
        "answer": result["answer"],
        "references": result["references"]
    }) 