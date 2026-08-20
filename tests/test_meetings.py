from __future__ import annotations

import time

from tests.helpers import make_wav_bytes


def _wait_for_status(client, meeting_id, timeout=10):
    for _ in range(timeout * 10):
        body = client.get(f"/meetings/{meeting_id}").json()
        if body["status"] not in ("pending", "processing"):
            return body
        time.sleep(0.1)
    raise TimeoutError("meeting pipeline did not finish in time")


def test_upload_and_mock_transcript(client):
    resp = client.post(
        "/meetings/upload",
        files={"file": ("meeting.wav", make_wav_bytes(20), "audio/wav")},
        data={"language": "en"},
    )
    assert resp.status_code == 200
    meeting_id = resp.json()["id"]

    status = _wait_for_status(client, meeting_id)
    assert status["status"] == "done"

    transcript = client.get(f"/meetings/{meeting_id}/transcript").json()
    assert transcript["transcript_source"] == "mock_asr"
    assert len(transcript["segments"]) > 0


def test_upload_with_sample_transcript_extracts_real_signal(client):
    text = (
        "We have decided to migrate to the new vendor. "
        "Priya will own the migration by next Friday. "
        "There is a risk that the audit deadline will be missed."
    )
    resp = client.post(
        "/meetings/upload",
        files={"file": ("meeting.wav", make_wav_bytes(10), "audio/wav")},
        data={"sample_transcript": text},
    )
    meeting_id = resp.json()["id"]
    status = _wait_for_status(client, meeting_id)
    assert status["status"] == "done"

    summary = client.get(f"/meetings/{meeting_id}/summary").json()
    assert len(summary["decisions"]) >= 1
    assert len(summary["action_items"]) >= 1
    assert len(summary["risks"]) >= 1

    provenance = client.get(f"/meetings/{meeting_id}/provenance").json()
    assert len(provenance["entries"]) >= 1

    pdf_resp = client.get(f"/meetings/{meeting_id}/provenance/export.pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"


def test_get_missing_meeting_404s(client):
    resp = client.get("/meetings/does-not-exist")
    assert resp.status_code == 404
