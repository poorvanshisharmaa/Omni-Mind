from __future__ import annotations

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import WrapMode
from fpdf.enums import XPos, YPos
from sqlmodel import Session

from app.config import settings
from app.models import Meeting
from app.storage.audit_log import list_for_meeting


def get_provenance_log(session: Session, meeting_id: str):
    return list_for_meeting(session, meeting_id)


def export_provenance_pdf(session: Session, meeting: Meeting) -> Path:
    entries = list_for_meeting(session, meeting.id)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Provenance Log - {meeting.filename}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Meeting ID: {meeting.id}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"Generated: {meeting.created_at.isoformat()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    if not entries:
        pdf.multi_cell(0, 6, "No decisions were logged for this meeting.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for entry in entries:
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, f"[{entry.timestamp:.1f}s] Decision", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(
            0, 6, entry.text.encode("latin-1", "replace").decode("latin-1"), new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(
            0, 6, f"Audio clip: {entry.audio_clip_url}",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT, wrapmode=WrapMode.CHAR,
        )
        pdf.ln(3)

    out_dir = settings.data_dir / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{meeting.id}-provenance.pdf"
    pdf.output(str(out_path))
    return out_path
