from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db import get_session
from app.storage.vector_store import search

router = APIRouter(tags=["search"])


@router.get("/search")
def search_endpoint(
    q: str = Query(..., min_length=1), top_k: int = Query(10, ge=1, le=50), session: Session = Depends(get_session)
):
    return {"query": q, "results": search(session, q, top_k=top_k)}
