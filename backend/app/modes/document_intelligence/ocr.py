from __future__ import annotations

from pathlib import Path


class OCRUnavailableError(RuntimeError):
    pass


def extract_text_from_image(path: Path) -> str:
    """Real OCR via pytesseract, when the `tesseract` binary is installed.

    Not available on this machine (no `tesseract` on PATH), so scanned
    image uploads raise a clear, honest error instead of fabricating text.
    Run `pip install pytesseract pillow` and `brew install tesseract` to
    enable this path.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise OCRUnavailableError(
            "OCR is not installed. Run `pip install pytesseract pillow` and "
            "`brew install tesseract` to enable scanned-image support."
        ) from exc

    try:
        return pytesseract.image_to_string(Image.open(path))
    except pytesseract.TesseractNotFoundError as exc:
        raise OCRUnavailableError(
            "The `tesseract` binary isn't installed. Run `brew install tesseract`."
        ) from exc
