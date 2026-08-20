from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, WebSocket
from sqlmodel import Session

from app.core.ingestion import save_upload
from app.db import get_session
from app.modes.translator.async_mode import translate_async
from app.modes.translator.glossary import add_term, list_terms, remove_term
from app.modes.translator.live_mode import run_live_translation
from app.storage.files import to_media_url

router = APIRouter(tags=["translator"])


@router.post("/translate/async")
async def translate_async_endpoint(
    source_lang: str = Form("auto"),
    target_lang: str = Form(...),
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    if not text and not audio:
        raise HTTPException(status_code=400, detail="Provide either `text` or an `audio` file")

    audio_path = save_upload(audio, "uploads") if audio else None
    translation = translate_async(
        session, text=text, audio_path=audio_path, source_lang=source_lang, target_lang=target_lang
    )
    return {
        "id": translation.id,
        "source_text": translation.source_text,
        "translated_text": translation.translated_text,
        "audio_url": to_media_url(translation.audio_path) if translation.audio_path else None,
    }


@router.websocket("/translate/live")
async def translate_live_endpoint(websocket: WebSocket, session: Session = Depends(get_session)):
    await run_live_translation(websocket, session)


@router.post("/translate/glossary")
def add_glossary_term(
    term: str = Form(...), note: Optional[str] = Form(None), session: Session = Depends(get_session)
):
    return add_term(session, term, note)


@router.get("/translate/glossary")
def get_glossary(session: Session = Depends(get_session)):
    return list_terms(session)


@router.delete("/translate/glossary/{term_id}")
def delete_glossary_term(term_id: str, session: Session = Depends(get_session)):
    if not remove_term(session, term_id):
        raise HTTPException(status_code=404, detail="Term not found")
    return {"deleted": True}
