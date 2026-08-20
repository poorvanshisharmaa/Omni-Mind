from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.ingestion import extract_document_text, save_upload
from app.core.pipeline import run_document_pipeline
from app.db import get_session
from app.models import Document, DocumentChapter
from app.storage.files import to_media_url

router = APIRouter(prefix="/documents", tags=["documents"])

_SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt", ".md"}


def _get_document_or_404(document_id: str, session: Session) -> Document:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    source_lang: str = Form("auto"),
    session: Session = Depends(get_session),
):
    path = save_upload(file, "uploads")
    if path.suffix.lower() not in _SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=501,
            detail=(
                f"'{path.suffix}' isn't supported yet. PDF/DOCX/TXT/MD extract real text; "
                "scanned images need OCR (tesseract), which isn't installed on this server."
            ),
        )

    document = Document(
        filename=file.filename or path.name,
        file_path=str(path),
        source_language=source_lang,
        target_language=target_lang,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    chapters = extract_document_text(path)
    for i, (heading, text) in enumerate(chapters):
        session.add(DocumentChapter(document_id=document.id, sort_order=i, heading=heading, original_text=text))
    session.commit()

    background_tasks.add_task(run_document_pipeline, document.id)
    return {"id": document.id, "status": document.status, "chapter_count": len(chapters)}


@router.get("")
def list_documents(session: Session = Depends(get_session)):
    return session.exec(select(Document).order_by(Document.created_at.desc())).all()


@router.get("/{document_id}")
def get_document(document_id: str, session: Session = Depends(get_session)):
    document = _get_document_or_404(document_id, session)
    chapters = session.exec(
        select(DocumentChapter).where(DocumentChapter.document_id == document_id).order_by(DocumentChapter.sort_order)
    ).all()
    return {
        "document": document,
        "chapters": [
            {"heading": c.heading, "original_text": c.original_text, "translated_text": c.translated_text}
            for c in chapters
        ],
    }


@router.get("/{document_id}/audio")
def get_document_audio(document_id: str, session: Session = Depends(get_session)):
    document = _get_document_or_404(document_id, session)
    chapters = session.exec(
        select(DocumentChapter).where(DocumentChapter.document_id == document_id).order_by(DocumentChapter.sort_order)
    ).all()
    return {
        "document_id": document.id,
        "status": document.status,
        "chapters": [
            {"heading": c.heading, "audio_url": to_media_url(c.audio_path) if c.audio_path else None}
            for c in chapters
        ],
    }
