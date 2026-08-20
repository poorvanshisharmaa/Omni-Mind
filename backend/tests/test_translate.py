from __future__ import annotations


def test_translate_text_with_glossary_lock(client):
    client.post("/translate/glossary", data={"term": "Trading Mandate"})

    resp = client.post(
        "/translate/async",
        data={
            "text": "The Trading Mandate was approved by the client.",
            "source_lang": "en",
            "target_lang": "fr",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Trading Mandate" in body["translated_text"]
    assert "approuvé" in body["translated_text"].lower()
    assert body["audio_url"].startswith("/media/")


def test_translate_requires_text_or_audio(client):
    resp = client.post("/translate/async", data={"target_lang": "fr"})
    assert resp.status_code == 400


def test_live_translate_websocket(client):
    with client.websocket_connect("/translate/live") as ws:
        ws.send_json({"text": "The team approved the report.", "source_lang": "en", "target_lang": "es"})
        reply = ws.receive_json()
        assert reply["type"] == "translation"
        assert "aprobado" in reply["translated_text"].lower()
