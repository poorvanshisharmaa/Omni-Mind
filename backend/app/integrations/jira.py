from __future__ import annotations

import httpx

from app.config import settings


def create_ticket(summary: str, assignee: str | None = None, due_date: str | None = None) -> dict:
    """Real Jira REST call when credentials are configured; a harmless,
    clearly-labeled no-op otherwise.
    """
    if not (settings.jira_base_url and settings.jira_email and settings.jira_api_token and settings.jira_project_key):
        return {"created": False, "reason": "Jira not configured", "ref": None}

    payload = {
        "fields": {
            "project": {"key": settings.jira_project_key},
            "summary": summary,
            "issuetype": {"name": "Task"},
            **({"duedate": due_date} if due_date else {}),
        }
    }
    try:
        resp = httpx.post(
            f"{settings.jira_base_url}/rest/api/3/issue",
            json=payload,
            auth=(settings.jira_email, settings.jira_api_token),
            timeout=10,
        )
        resp.raise_for_status()
        return {"created": True, "ref": resp.json().get("key")}
    except httpx.HTTPError as exc:
        return {"created": False, "reason": str(exc), "ref": None}
