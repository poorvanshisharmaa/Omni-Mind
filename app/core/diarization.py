from __future__ import annotations

import random

SPEAKER_POOL = ["Speaker A", "Speaker B", "Speaker C", "Speaker D"]


def assign_speakers(count: int, rng: random.Random, min_speakers: int = 2, max_speakers: int = 4) -> list[str]:
    """Round-robin speaker labels across `count` segments.

    Stands in for `pyannote.audio` diarization, which needs a gated
    HuggingFace token and real multi-speaker audio to do real speaker
    clustering. Swap this out behind the same signature once that's wired up.
    """
    n_speakers = rng.randint(min_speakers, min(max_speakers, len(SPEAKER_POOL)))
    speakers = SPEAKER_POOL[:n_speakers]
    return [speakers[i % n_speakers] for i in range(count)]
