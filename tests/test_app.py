"""Offline tests for the FastAPI app via the WebSocket TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient

from speech_to_text_streaming.app import END_OF_UTTERANCE, create_app
from speech_to_text_streaming.audio import tone_frame


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["provider"] == "fake"
    assert "version" in body


def test_websocket_streams_partial_and_final() -> None:
    client = TestClient(create_app("fake"))
    with client.websocket_connect("/ws/transcribe") as ws:
        ws.send_bytes(tone_frame(1600))  # one word at default samples_per_word
        partial = ws.receive_json()
        assert partial["type"] == "partial"
        assert partial["text"]

        ws.send_text(END_OF_UTTERANCE)
        final = ws.receive_json()
        assert final["type"] == "final"
        assert final["text"]


def test_websocket_final_without_partial() -> None:
    client = TestClient(create_app("fake"))
    with client.websocket_connect("/ws/transcribe") as ws:
        # Less than one word: no partial should be emitted before final.
        ws.send_bytes(tone_frame(800))
        ws.send_text(END_OF_UTTERANCE)
        final = ws.receive_json()
        assert final["type"] == "final"


def test_websocket_multiple_words_accumulate() -> None:
    client = TestClient(create_app("fake"))
    with client.websocket_connect("/ws/transcribe") as ws:
        ws.send_bytes(tone_frame(1600))
        first = ws.receive_json()
        ws.send_bytes(tone_frame(1600))
        second = ws.receive_json()
        assert len(second["text"].split()) == len(first["text"].split()) + 1
        ws.send_text(END_OF_UTTERANCE)
        final = ws.receive_json()
        assert final["type"] == "final"
