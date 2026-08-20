from __future__ import annotations

from sqlmodel import Session, select

from app.models import GlossaryTerm


def add_term(session: Session, term: str, note: str | None = None) -> GlossaryTerm:
    existing = session.exec(select(GlossaryTerm).where(GlossaryTerm.term == term)).first()
    if existing:
        return existing
    entry = GlossaryTerm(term=term, note=note)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def list_terms(session: Session) -> list[GlossaryTerm]:
    return session.exec(select(GlossaryTerm)).all()


def term_set(session: Session) -> set[str]:
    return {t.term for t in list_terms(session)}


def remove_term(session: Session, term_id: str) -> bool:
    entry = session.get(GlossaryTerm, term_id)
    if not entry:
        return False
    session.delete(entry)
    session.commit()
    return True
