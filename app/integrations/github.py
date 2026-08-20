from __future__ import annotations

import httpx

from app.config import settings


def create_issue(title: str, assignee: str | None = None) -> dict:
    """Real GitHub Issues API call when credentials are configured; a
    harmless, clearly-labeled no-op otherwise.
    """
    if not (settings.github_token and settings.github_repo):
        return {"created": False, "reason": "GitHub not configured", "ref": None}
    try:
        resp = httpx.post(
            f"https://api.github.com/repos/{settings.github_repo}/issues",
            json={"title": title},
            headers={"Authorization": f"Bearer {settings.github_token}", "Accept": "application/vnd.github+json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"created": True, "ref": f"#{data.get('number')}"}
    except httpx.HTTPError as exc:
        return {"created": False, "reason": str(exc), "ref": None}
