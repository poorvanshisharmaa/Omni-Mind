from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class Meeting(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    filename: str
    audio_path: str
    duration_seconds: float = 0.0
    language_hint: Optional[str] = None
    transcript_source: str = "mock_asr"  # "mock_asr" | "user_provided"
    status: JobStatus = JobStatus.pending
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)


class TranscriptSegment(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    index: int
    speaker: str
    start_time: float
    end_time: float
    language: str
    text: str


class Decision(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    segment_id: Optional[str] = Field(default=None, foreign_key="transcriptsegment.id")
    text: str
    speaker: str
    timestamp: float


class ActionItem(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    segment_id: Optional[str] = Field(default=None, foreign_key="transcriptsegment.id")
    task: str
    owner: str
    deadline: Optional[str] = None
    status: str = "open"
    ticket_ref: Optional[str] = None
    timestamp: float


class Risk(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    segment_id: Optional[str] = Field(default=None, foreign_key="transcriptsegment.id")
    text: str
    severity: str
    timestamp: float


class ProvenanceEntry(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    decision_id: Optional[str] = Field(default=None, foreign_key="decision.id")
    timestamp: float
    text: str
    audio_clip_url: str
    created_at: datetime = Field(default_factory=utcnow)


class Document(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    filename: str
    file_path: str
    source_language: str = "auto"
    target_language: str
    status: JobStatus = JobStatus.pending
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)


class DocumentChapter(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    sort_order: int
    heading: str
    original_text: str
    translated_text: Optional[str] = None
    audio_path: Optional[str] = None


class Translation(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    mode: str = "async"
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    audio_path: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)


class GlossaryTerm(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    term: str = Field(index=True, unique=True)
    note: Optional[str] = None
