from __future__ import annotations

from datetime import date

from sqlmodel import Session, select

from app.integrations import github as github_client
from app.integrations import jira as jira_client
from app.integrations import slack as slack_client
from app.models import ActionItem


def create_tickets_for_action_items(session: Session, meeting_id: str) -> None:
    """Ticket creation + notification agent: tries Jira first, falls back
    to GitHub, then pings Slack — matches the spec's "execution integration"
    step. Each integration degrades gracefully when unconfigured.
    """
    items = session.exec(select(ActionItem).where(ActionItem.meeting_id == meeting_id)).all()
    for item in items:
        result = jira_client.create_ticket(summary=item.task, assignee=item.owner, due_date=item.deadline)
        if not result.get("created"):
            result = github_client.create_issue(title=item.task, assignee=item.owner)
        item.ticket_ref = result.get("ref")
        session.add(item)

        due_note = f" (due {item.deadline})" if item.deadline else ""
        slack_client.notify(f"New action item for {item.owner}: {item.task}{due_note}")
    session.commit()


def escalate_overdue(session: Session, meeting_id: str) -> list[ActionItem]:
    """Follow-up agent: flags open action items past their deadline.

    A cron job would call this on a schedule per the spec; here it's a
    plain function an endpoint or scheduler can call on demand.
    """
    items = session.exec(
        select(ActionItem).where(ActionItem.meeting_id == meeting_id, ActionItem.status == "open")
    ).all()
    overdue = []
    for item in items:
        if item.deadline:
            try:
                if date.fromisoformat(item.deadline) < date.today():
                    overdue.append(item)
            except ValueError:
                pass
    return overdue
