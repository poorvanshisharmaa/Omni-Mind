from __future__ import annotations

import time


def _wait_for_status(client, document_id, timeout=10):
    for _ in range(timeout * 10):
        body = client.get(f"/documents/{document_id}").json()
        status = body["document"]["status"]
        if status not in ("pending", "processing"):
            return body
        time.sleep(0.1)
    raise TimeoutError("document pipeline did not finish in time")


def test_upload_txt_document_translates_and_narrates(client):
    content = (
        b"Project Update\n"
        b"The team approved the budget this week.\n\n"
        b"Risks\n"
        b"There is a risk in the client timeline.\n"
    )
    resp = client.post(
        "/documents/upload",
        files={"file": ("update.txt", content, "text/plain")},
        data={"target_lang": "fr", "source_lang": "en"},
    )
    assert resp.status_code == 200
    document_id = resp.json()["id"]

    result = _wait_for_status(client, document_id)
    assert result["document"]["status"] == "done"
    assert len(result["chapters"]) >= 1
    assert result["chapters"][0]["translated_text"]

    audio = client.get(f"/documents/{document_id}/audio").json()
    assert audio["chapters"][0]["audio_url"].startswith("/media/")


def test_upload_unsupported_type_returns_501(client):
    resp = client.post(
        "/documents/upload",
        files={"file": ("scan.png", b"\x89PNG\r\n", "image/png")},
        data={"target_lang": "fr"},
    )
    assert resp.status_code == 501
