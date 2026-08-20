from __future__ import annotations

import httpx

from app.config import settings


def notify(message: str) -> dict:
    """Real Slack incoming-webhook POST when configured; a harmless,
    clearly-labeled no-op otherwise.
    """
    if not settings.slack_webhook_url:
        return {"sent": False, "reason": "Slack not configured"}
    try:
        resp = httpx.post(settings.slack_webhook_url, json={"text": message}, timeout=10)
        resp.raise_for_status()
        return {"sent": True}
    except httpx.HTTPError as exc:
        return {"sent": False, "reason": str(exc)}
