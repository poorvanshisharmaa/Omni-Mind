from __future__ import annotations

from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.core.translation import get_translation_engine
from app.modes.translator.glossary import term_set


async def run_live_translation(websocket: WebSocket, session: Session) -> None:
    """Real-time speech-to-speech translation stream.

    No live ASR/TTS here (that would need real-time Whisper + streaming
    XTTS) — the client sends already-transcribed text chunks and gets back
    translated text over the same socket. Swap in real streaming ASR/TTS
    behind this same message loop later without changing the wire protocol.
    """
    await websocket.accept()
    engine = get_translation_engine()
    glossary = term_set(session)
    try:
        while True:
            payload = await websocket.receive_json()
            text = payload.get("text", "")
            target_lang = payload.get("target_lang", "en")
            source_lang = payload.get("source_lang", "auto")
            translated = engine.translate(text, source_lang, target_lang, glossary)
            await websocket.send_json(
                {
                    "type": "translation",
                    "source_text": text,
                    "translated_text": translated,
                    "target_lang": target_lang,
                }
            )
    except WebSocketDisconnect:
        return
