from __future__ import annotations

from sqlmodel import Session, select

from app.models import ProvenanceEntry


def record(session: Session, entry: ProvenanceEntry) -> ProvenanceEntry:
    """Append-only: provenance entries are never updated or deleted."""
    session.add(entry)
    return entry


def list_for_meeting(session: Session, meeting_id: str) -> list[ProvenanceEntry]:
    return session.exec(
        select(ProvenanceEntry)
        .where(ProvenanceEntry.meeting_id == meeting_id)
        .order_by(ProvenanceEntry.timestamp)
    ).all()
