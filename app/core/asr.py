from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from app.core.diarization import assign_speakers


@dataclass
class RawSegment:
    speaker: str
    start: float
    end: float
    language: str
    text: str


# Template bank chosen to give the reasoning engine real signal to extract:
# decision language, action-item ownership/deadline phrasing, and risk
# language, including a couple of Hinglish code-switched lines per the
# spec's differentiation angle.
_TEMPLATE_BANK: list[tuple[str, str]] = [
    ("en", "Let's review the quarterly compliance numbers before we move on."),
    ("en", "We have decided to migrate the trade settlement pipeline to the new vendor."),
    ("en", "Priya will own the vendor migration and deliver a rollout plan by next Friday."),
    ("en", "There's a risk that the legacy system won't be decommissioned in time for the audit."),
    ("hi-en", "Toh basically hum ye decision le rahe hain ki client onboarding ko fully digital kar denge."),
    ("en", "Action item: Raj owns the KYC automation ticket, deadline is March 15."),
    ("en", "I'm concerned about the data residency requirement for the Mumbai region."),
    ("en", "Agreed, let's approve the budget for the new fraud detection model."),
    ("hi-en", "Ek open question hai, regulatory approval abhi tak nahi mila hai, that's a blocker."),
    ("en", "Let's park that discussion and come back to it after the risk review."),
    ("en", "Meera, can you take ownership of the vendor contract review by end of week?"),
    ("en", "We approved moving the go-live date to next month given the outstanding risks."),
    ("en", "The unresolved question is who signs off on the final compliance report."),
    ("en", "Sure, sounds good, let's move to the next agenda item."),
    ("en", "Decision made: we will not proceed with the third-party integration this quarter."),
]


class ASREngine:
    """Interface every ASR backend implements. Swap `MockASREngine` for a
    real `faster-whisper` / `openai-whisper` wrapper without touching callers.
    """

    def transcribe(
        self, audio_path: str, duration_seconds: float, language_hint: str | None
    ) -> list[RawSegment]:
        raise NotImplementedError


class MockASREngine(ASREngine):
    """Deterministic, template-based transcript generator.

    Not a real speech recognizer — there is no ML model here. It exists so
    the rest of the pipeline (decision/action-item extraction, provenance
    logging, search) has real text to operate on, without requiring a GPU
    or a multi-gigabyte model download. Output is seeded from the audio
    file's own path, so the same upload always produces the same transcript.
    """

    def transcribe(
        self, audio_path: str, duration_seconds: float, language_hint: str | None
    ) -> list[RawSegment]:
        seed = int(hashlib.sha256(audio_path.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        num_segments = max(4, min(24, int(duration_seconds // 8) or 6))
        lines = rng.sample(_TEMPLATE_BANK, k=min(num_segments, len(_TEMPLATE_BANK)))
        while len(lines) < num_segments:
            lines.append(rng.choice(_TEMPLATE_BANK))
        rng.shuffle(lines)

        speaker_labels = assign_speakers(num_segments, rng)

        segments: list[RawSegment] = []
        cursor = 0.0
        step = max((duration_seconds or num_segments * 5) / num_segments, 3.0)
        for i, (lang, text) in enumerate(lines):
            start = round(cursor, 2)
            end = round(min(cursor + step * rng.uniform(0.6, 1.0), duration_seconds or (cursor + step)), 2)
            segments.append(
                RawSegment(
                    speaker=speaker_labels[i],
                    start=start,
                    end=max(end, start + 1.0),
                    language=language_hint or lang,
                    text=text,
                )
            )
            cursor += step
        return segments


def get_asr_engine() -> ASREngine:
    return MockASREngine()
