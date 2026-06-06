"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

FastAPI application exposing a realtime speech-to-text streaming WebSocket endpoint
plus a ``/health`` route.

Protocol (WebSocket ``/ws/transcribe``):

* The client sends **binary** messages containing raw little-endian 16-bit PCM mono
  audio chunks.
* The client sends the **text** message ``"__end__"`` to signal end-of-utterance.
* The server replies with JSON messages of the form
  ``{"type": "partial" | "final", "text": "..."}``.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from speech_to_text_streaming import __version__
from speech_to_text_streaming.providers import load_provider
from speech_to_text_streaming.session import StreamingSession

END_OF_UTTERANCE = "__end__"


def create_app(provider_name: str | None = None) -> FastAPI:
    """Build the FastAPI application.

    Args:
        provider_name: STT provider to use. Defaults to the ``STT_PROVIDER``
            environment variable, or ``"fake"`` when unset.

    Returns:
        A configured :class:`fastapi.FastAPI` instance.
    """
    selected = provider_name or os.environ.get("STT_PROVIDER", "fake")
    app = FastAPI(
        title="Speech To Text Streaming",
        version=__version__,
        summary="Realtime speech-to-text streaming server by Viprasol Tech.",
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "version": __version__, "provider": selected}

    @app.websocket("/ws/transcribe")
    async def transcribe(websocket: WebSocket) -> None:
        await websocket.accept()
        session = StreamingSession(provider=load_provider(selected))
        try:
            while True:
                message = await websocket.receive()
                if message.get("type") == "websocket.disconnect":
                    return
                if (data := message.get("bytes")) is not None:
                    partial = session.push(data)
                    if partial is not None:
                        await websocket.send_json({"type": "partial", "text": partial.text})
                elif (text := message.get("text")) is not None and text == END_OF_UTTERANCE:
                    final = session.close()
                    await websocket.send_json({"type": "final", "text": final.text})
                    break
        except WebSocketDisconnect:
            return
        finally:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()

    return app


app = create_app()


def run() -> None:  # pragma: no cover - thin uvicorn entrypoint
    """Run the server with uvicorn (console-script entrypoint)."""
    import uvicorn

    uvicorn.run(
        "speech_to_text_streaming.app:app",
        host=os.environ.get("STT_HOST", "0.0.0.0"),
        port=int(os.environ.get("STT_PORT", "8000")),
    )
