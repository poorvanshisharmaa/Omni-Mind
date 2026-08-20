from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.asr import RawSegment

try:
    from dateutil import parser as dateutil_parser
except ImportError:  # pragma: no cover
    dateutil_parser = None


@dataclass
class ExtractedDecision:
    text: str
    speaker: str
    timestamp: float


@dataclass
class ExtractedActionItem:
    task: str
    owner: str
    deadline: str | None
    timestamp: float


@dataclass
class ExtractedRisk:
    text: str
    severity: str
    timestamp: float


@dataclass
class ExtractionResult:
    decisions: list[ExtractedDecision]
    action_items: list[ExtractedActionItem]
    risks: list[ExtractedRisk]


_DECISION_RE = re.compile(r"\b(we (have )?decided|decision( made| is)?:?|agreed to|approved|approve)\b", re.I)
_ACTION_RE = re.compile(r"\b(action item|will own|owns? this|take ownership|responsible for|can you)\b", re.I)
_RISK_RE = re.compile(r"\b(risk|concern(ed)?|blocker|unresolved|open question)\b", re.I)
_OWNER_RE = re.compile(r"\b([A-Z][a-z]+)\b(?=[,]? (?:will own|owns|can you|take ownership))")
_DEADLINE_HINT_RE = re.compile(
    r"\b(by\s+[A-Za-z]+\s*\d{0,2}|deadline is\s+[A-Za-z]+\s*\d{0,2}|end of week|EOD|next week|next month)\b",
    re.I,
)

_HIGH_SEVERITY_WORDS = ("blocker", "unresolved", "won't", "not proceed")


class ReasoningEngine:
    """Interface every reasoning/extraction backend implements. Swap
    `RuleBasedReasoningEngine` for a real Qwen2.5 prompt-based extractor
    without touching callers.
    """

    def extract(self, segments: list[RawSegment]) -> ExtractionResult:
        raise NotImplementedError


class RuleBasedReasoningEngine(ReasoningEngine):
    """Regex/keyword extraction over transcript text.

    Not an LLM — there's no model here, just pattern matching. It runs on
    whatever text it's given (mock-generated or user-supplied), so plugging
    in a real ASR engine later doesn't require touching this module.
    """

    def extract(self, segments: list[RawSegment]) -> ExtractionResult:
        decisions: list[ExtractedDecision] = []
        action_items: list[ExtractedActionItem] = []
        risks: list[ExtractedRisk] = []

        for seg in segments:
            text = seg.text
            if _DECISION_RE.search(text):
                decisions.append(ExtractedDecision(text=text, speaker=seg.speaker, timestamp=seg.start))
            if _ACTION_RE.search(text):
                owner_match = _OWNER_RE.search(text)
                owner = owner_match.group(1) if owner_match else seg.speaker
                deadline = self._extract_deadline(text)
                action_items.append(
                    ExtractedActionItem(task=text, owner=owner, deadline=deadline, timestamp=seg.start)
                )
            if _RISK_RE.search(text):
                severity = "high" if any(w in text.lower() for w in _HIGH_SEVERITY_WORDS) else "medium"
                risks.append(ExtractedRisk(text=text, severity=severity, timestamp=seg.start))

        return ExtractionResult(decisions=decisions, action_items=action_items, risks=risks)

    @staticmethod
    def _extract_deadline(text: str) -> str | None:
        hint = _DEADLINE_HINT_RE.search(text)
        if not hint:
            return None
        if dateutil_parser is None:
            return hint.group(0)
        try:
            parsed = dateutil_parser.parse(hint.group(0), fuzzy=True, default=datetime.now(timezone.utc))
            return parsed.date().isoformat()
        except (ValueError, OverflowError):
            return hint.group(0)


def get_reasoning_engine() -> ReasoningEngine:
    return RuleBasedReasoningEngine()
