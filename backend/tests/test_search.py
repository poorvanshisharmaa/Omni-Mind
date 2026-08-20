from __future__ import annotations

import time

from tests.helpers import make_wav_bytes


def test_search_across_meetings_and_documents(client):
    client.post(
        "/meetings/upload",
        files={"file": ("m.wav", make_wav_bytes(5), "audio/wav")},
        data={"sample_transcript": "We decided to approve the fraud detection budget this quarter."},
    )
    client.post(
        "/documents/upload",
        files={"file": ("d.txt", b"Fraud detection budget details for the quarter.", "text/plain")},
        data={"target_lang": "fr"},
    )
    time.sleep(0.3)

    resp = client.get("/search", params={"q": "fraud detection budget"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) >= 1
