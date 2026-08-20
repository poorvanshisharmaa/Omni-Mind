from __future__ import annotations

from pathlib import Path

from app.config import settings


def to_media_url(path: str | Path) -> str:
    """Convert an absolute path under data/ into a URL served at /media."""
    rel = Path(path).resolve().relative_to(settings.data_dir.resolve())
    return f"/media/{rel.as_posix()}"
