from __future__ import annotations

from pathlib import Path

from app.core.tts import TTSEngine
from app.models import DocumentChapter


def narrate_chapter(tts: TTSEngine, chapter: DocumentChapter, language: str, audio_dir: Path) -> Path:
    out_path = audio_dir / f"{chapter.sort_order:02d}.wav"
    tts.synth(chapter.translated_text or chapter.original_text, language, out_path)
    return out_path
