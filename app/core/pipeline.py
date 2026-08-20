from __future__ import annotations

from sqlmodel import Session, select

from app.config import settings
from app.core.asr import RawSegment, get_asr_engine
from app.core.reasoning import get_reasoning_engine
from app.core.translation import get_translation_engine
from app.core.tts import get_tts_engine
from app.db import engine
from app.models import (
    ActionItem,
    Decision,
    Document,
    DocumentChapter,
    GlossaryTerm,
    JobStatus,
    Meeting,
    ProvenanceEntry,
    Risk,
    TranscriptSegment,
)
from app.modes.document_intelligence.narrator import narrate_chapter
from app.modes.meeting_intelligence.agents import create_tickets_for_action_items
from app.storage.audit_log import record
from app.storage.files import to_media_url


def run_meeting_pipeline(meeting_id: str, sample_transcript: str | None = None) -> None:
    with Session(engine) as session:
        meeting = session.get(Meeting, meeting_id)
        if meeting is None:
            return
        try:
            meeting.status = JobStatus.processing
            session.add(meeting)
            session.commit()

            if sample_transcript:
                raw_segments = [
                    RawSegment(
                        speaker="Speaker A",
                        start=0.0,
                        end=meeting.duration_seconds or 10.0,
                        language=meeting.language_hint or "en",
                        text=sample_transcript,
                    )
                ]
                meeting.transcript_source = "user_provided"
            else:
                raw_segments = get_asr_engine().transcribe(
                    meeting.audio_path, meeting.duration_seconds, meeting.language_hint
                )
                meeting.transcript_source = "mock_asr"

            segments: list[TranscriptSegment] = []
            for i, raw in enumerate(raw_segments):
                seg = TranscriptSegment(
                    meeting_id=meeting.id,
                    index=i,
                    speaker=raw.speaker,
                    start_time=raw.start,
                    end_time=raw.end,
                    language=raw.language,
                    text=raw.text,
                )
                session.add(seg)
                segments.append(seg)
            session.add(meeting)
            session.commit()

            extraction = get_reasoning_engine().extract(raw_segments)
            seg_by_start = {raw.start: seg for raw, seg in zip(raw_segments, segments)}

            for d in extraction.decisions:
                seg = seg_by_start.get(d.timestamp)
                decision = Decision(
                    meeting_id=meeting.id,
                    segment_id=seg.id if seg else None,
                    text=d.text,
                    speaker=d.speaker,
                    timestamp=d.timestamp,
                )
                session.add(decision)
                clip_url = to_media_url(meeting.audio_path) + f"#t={d.timestamp:.1f}"
                record(
                    session,
                    ProvenanceEntry(
                        meeting_id=meeting.id,
                        decision_id=decision.id,
                        timestamp=d.timestamp,
                        text=d.text,
                        audio_clip_url=clip_url,
                    ),
                )

            for a in extraction.action_items:
                seg = seg_by_start.get(a.timestamp)
                session.add(
                    ActionItem(
                        meeting_id=meeting.id,
                        segment_id=seg.id if seg else None,
                        task=a.task,
                        owner=a.owner,
                        deadline=a.deadline,
                        timestamp=a.timestamp,
                    )
                )

            for r in extraction.risks:
                seg = seg_by_start.get(r.timestamp)
                session.add(
                    Risk(
                        meeting_id=meeting.id,
                        segment_id=seg.id if seg else None,
                        text=r.text,
                        severity=r.severity,
                        timestamp=r.timestamp,
                    )
                )

            session.commit()
            create_tickets_for_action_items(session, meeting.id)

            meeting.status = JobStatus.done
            session.add(meeting)
            session.commit()
        except Exception as exc:  # pragma: no cover - defensive
            meeting.status = JobStatus.failed
            meeting.error = str(exc)
            session.add(meeting)
            session.commit()


def run_document_pipeline(document_id: str) -> None:
    with Session(engine) as session:
        document = session.get(Document, document_id)
        if document is None:
            return
        try:
            document.status = JobStatus.processing
            session.add(document)
            session.commit()

            chapters = session.exec(
                select(DocumentChapter)
                .where(DocumentChapter.document_id == document.id)
                .order_by(DocumentChapter.sort_order)
            ).all()

            translator = get_translation_engine()
            tts = get_tts_engine()
            glossary_terms = {t.term for t in session.exec(select(GlossaryTerm)).all()}
            audio_dir = settings.data_dir / "audio" / document.id
            audio_dir.mkdir(parents=True, exist_ok=True)

            for chapter in chapters:
                chapter.translated_text = translator.translate(
                    chapter.original_text, document.source_language, document.target_language, glossary_terms
                )
                out_path = narrate_chapter(tts, chapter, document.target_language, audio_dir)
                chapter.audio_path = str(out_path)
                session.add(chapter)

            session.commit()
            document.status = JobStatus.done
            session.add(document)
            session.commit()
        except Exception as exc:  # pragma: no cover - defensive
            document.status = JobStatus.failed
            document.error = str(exc)
            session.add(document)
            session.commit()
