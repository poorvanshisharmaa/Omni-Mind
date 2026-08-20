from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select

from app.models import Document, DocumentChapter, Meeting, TranscriptSegment


@dataclass
class SearchResult:
    ref_type: str
    ref_id: str
    title: str
    snippet: str
    score: float


def _corpus(session: Session) -> list[SearchResult]:
    entries: list[SearchResult] = []

    for meeting in session.exec(select(Meeting)).all():
        segments = session.exec(
            select(TranscriptSegment).where(TranscriptSegment.meeting_id == meeting.id)
        ).all()
        text = " ".join(s.text for s in segments)
        if text.strip():
            entries.append(SearchResult("meeting", meeting.id, meeting.filename, text[:280], 0.0))

    for document in session.exec(select(Document)).all():
        chapters = session.exec(
            select(DocumentChapter).where(DocumentChapter.document_id == document.id)
        ).all()
        text = " ".join(c.original_text for c in chapters)
        if text.strip():
            entries.append(SearchResult("document", document.id, document.filename, text[:280], 0.0))

    return entries


def search(session: Session, query: str, top_k: int = 10) -> list[SearchResult]:
    """TF-IDF lexical search across ingested meetings and documents.

    This is a real, working ranking algorithm — not a mock — but it's
    lexical, not semantic, so it won't match paraphrases across languages
    the way the spec's BGE-M3 embedding search would. Swap in a real
    multilingual sentence-embedding model + a persisted index behind this
    same `search()` signature to get genuine cross-lingual retrieval at
    scale; recomputing TF-IDF per query is fine at demo/small-corpus size.
    """
    corpus = _corpus(session)
    if not corpus or not query.strip():
        return []

    texts = [c.snippet for c in corpus] + [query]
    vectorizer = TfidfVectorizer(max_features=4096)
    matrix = vectorizer.fit_transform(texts)
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    ranked = sorted(zip(corpus, scores), key=lambda pair: pair[1], reverse=True)
    results: list[SearchResult] = []
    for entry, score in ranked[:top_k]:
        if score <= 0:
            continue
        results.append(SearchResult(entry.ref_type, entry.ref_id, entry.title, entry.snippet, float(score)))
    return results
