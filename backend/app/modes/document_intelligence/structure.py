"""Chapter/heading detection lives in `app.core.ingestion.extract_document_text`
to keep parsing and chaptering as a single pass over the file. Re-exported
here to match the module layout in the product spec.
"""
from app.core.ingestion import extract_document_text

__all__ = ["extract_document_text"]
