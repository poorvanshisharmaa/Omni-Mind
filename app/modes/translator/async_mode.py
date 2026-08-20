from __future__ import annotations

import uuid
from pathlib import Path

from sqlmodel import Session

from app.config import settings
from app.core.asr import get_asr_engine
from app.core.ingestion import probe_audio_duration
from app.core.translation import get_translation_engine
from app.core.tts import get_tts_engine
from app.models import Translation
from app.modes.translator.glossary import term_set


def translate_async(
    session: Session,
    *,
    text: str | None,
    audio_path: Path | None,
    source_lang: str,
    target_lang: str,
) -> Translation:
    if audio_path is not None:
        duration = probe_audio_duration(audio_path)
        raw_segments = get_asr_engine().transcribe(str(audio_path), duration, source_lang)
        source_text = " ".join(seg.text for seg in raw_segments)
    else:
        source_text = text or ""

    glossary = term_set(session)
    translated_text = get_translation_engine().translate(source_text, source_lang, target_lang, glossary)

    audio_dir = settings.data_dir / "audio" / "translations"
    audio_dir.mkdir(parents=True, exist_ok=True)
    out_path = audio_dir / f"{uuid.uuid4().hex}.wav"
    get_tts_engine().synth(translated_text, target_lang, out_path)

    translation = Translation(
        mode="async",
        source_language=source_lang,
        target_language=target_lang,
        source_text=source_text,
        translated_text=translated_text,
        audio_path=str(out_path),
    )
    session.add(translation)
    session.commit()
    session.refresh(translation)
    return translation
