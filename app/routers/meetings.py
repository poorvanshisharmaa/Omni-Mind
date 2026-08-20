from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.core.ingestion import probe_audio_duration, save_upload
from app.core.pipeline import run_meeting_pipeline
from app.db import get_session
from app.models import ActionItem, Decision, Meeting, Risk, TranscriptSegment
from app.modes.meeting_intelligence.provenance import export_provenance_pdf
from app.storage.audit_log import list_for_meeting

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _get_meeting_or_404(meeting_id: str, session: Session) -> Meeting:
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("/upload")
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    sample_transcript: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    path = save_upload(file, "uploads")
    duration = probe_audio_duration(path)
    meeting = Meeting(
        filename=file.filename or path.name,
        audio_path=str(path),
        duration_seconds=duration,
        language_hint=language,
    )
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    background_tasks.add_task(run_meeting_pipeline, meeting.id, sample_transcript)
    return {"id": meeting.id, "status": meeting.status, "duration_seconds": meeting.duration_seconds}


@router.get("")
def list_meetings(session: Session = Depends(get_session)):
    return session.exec(select(Meeting).order_by(Meeting.created_at.desc())).all()


@router.get("/{meeting_id}")
def get_meeting(meeting_id: str, session: Session = Depends(get_session)):
    return _get_meeting_or_404(meeting_id, session)


@router.get("/{meeting_id}/transcript")
def get_transcript(meeting_id: str, session: Session = Depends(get_session)):
    meeting = _get_meeting_or_404(meeting_id, session)
    segments = session.exec(
        select(TranscriptSegment).where(TranscriptSegment.meeting_id == meeting_id).order_by(TranscriptSegment.index)
    ).all()
    return {
        "meeting_id": meeting.id,
        "status": meeting.status,
        "transcript_source": meeting.transcript_source,
        "segments": segments,
    }


@router.get("/{meeting_id}/summary")
def get_summary(meeting_id: str, session: Session = Depends(get_session)):
    meeting = _get_meeting_or_404(meeting_id, session)
    decisions = session.exec(
        select(Decision).where(Decision.meeting_id == meeting_id).order_by(Decision.timestamp)
    ).all()
    action_items = session.exec(
        select(ActionItem).where(ActionItem.meeting_id == meeting_id).order_by(ActionItem.timestamp)
    ).all()
    risks = session.exec(select(Risk).where(Risk.meeting_id == meeting_id).order_by(Risk.timestamp)).all()
    return {
        "meeting_id": meeting.id,
        "status": meeting.status,
        "decisions": decisions,
        "action_items": action_items,
        "risks": risks,
    }


@router.get("/{meeting_id}/provenance")
def get_provenance(meeting_id: str, session: Session = Depends(get_session)):
    meeting = _get_meeting_or_404(meeting_id, session)
    entries = list_for_meeting(session, meeting_id)
    return {
        "meeting_id": meeting.id,
        "entries": entries,
        "export_pdf_url": f"/meetings/{meeting_id}/provenance/export.pdf",
    }


@router.get("/{meeting_id}/provenance/export.pdf")
def export_provenance(meeting_id: str, session: Session = Depends(get_session)):
    meeting = _get_meeting_or_404(meeting_id, session)
    path = export_provenance_pdf(session, meeting)
    return FileResponse(path, media_type="application/pdf", filename=path.name)
