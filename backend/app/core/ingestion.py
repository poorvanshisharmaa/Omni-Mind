from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

import docx
from fastapi import UploadFile
from pypdf import PdfReader

from app.config import settings

try:
    from mutagen import File as MutagenFile
except ImportError:  # pragma: no cover
    MutagenFile = None


def save_upload(file: UploadFile, subdir: str) -> Path:
    dest_dir = settings.data_dir / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload").suffix
    dest = dest_dir / f"{uuid.uuid4().hex}{suffix}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return dest


def probe_audio_duration(path: Path) -> float:
    if MutagenFile is not None:
        try:
            audio = MutagenFile(str(path))
            if audio is not None and audio.info is not None:
                return float(audio.info.length)
        except Exception:
            pass
    # Fallback: assume a 128kbps encode so an unrecognized format still gets
    # a plausible, non-zero duration instead of crashing the pipeline.
    size_bits = path.stat().st_size * 8
    return max(1.0, size_bits / 128_000)


_HEADING_RE = re.compile(r"^[A-Z][A-Za-z0-9 ,'&-]{2,60}$")


def extract_document_text(path: Path) -> list[tuple[str, str]]:
    """Returns a list of (heading, text) chapters, extracted for real from
    the uploaded file — no ML, just format parsing.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    return _extract_plaintext(path)


def _extract_pdf(path: Path) -> list[tuple[str, str]]:
    reader = PdfReader(str(path))
    chapters: list[tuple[str, str]] = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            chapters.append((f"Page {i + 1}", text))
    return chapters or [("Document", "")]


def _extract_docx(path: Path) -> list[tuple[str, str]]:
    document = docx.Document(str(path))
    chapters: list[tuple[str, str]] = []
    current_heading = "Introduction"
    current_lines: list[str] = []

    def flush() -> None:
        if current_lines:
            chapters.append((current_heading, "\n".join(current_lines).strip()))

    for para in document.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if para.style is not None and para.style.name.lower().startswith("heading"):
            flush()
            current_heading = text
            current_lines = []
        else:
            current_lines.append(text)
    flush()
    return chapters or [("Document", "")]


def _extract_plaintext(path: Path) -> list[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()
    chapters: list[tuple[str, str]] = []
    current_heading = "Document"
    current_lines: list[str] = []

    def flush() -> None:
        if current_lines:
            chapters.append((current_heading, "\n".join(current_lines).strip()))

    for line in lines:
        stripped = line.strip()
        if stripped and _HEADING_RE.match(stripped) and len(stripped.split()) <= 8:
            flush()
            current_heading = stripped
            current_lines = []
        elif stripped:
            current_lines.append(stripped)
    flush()
    return chapters or [("Document", raw.strip())]
