"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

Realtime speech-to-text streaming server: a FastAPI WebSocket endpoint that accepts
audio chunks and emits partial and final transcripts, backed by a pluggable STT
provider with a deterministic offline fake recognizer.
"""

from __future__ import annotations

from speech_to_text_streaming.providers import (
    FakeSTT,
    STTProvider,
    Transcript,
    load_provider,
)
from speech_to_text_streaming.session import StreamingSession

__all__ = [
    "FakeSTT",
    "STTProvider",
    "StreamingSession",
    "Transcript",
    "__version__",
    "load_provider",
]

__version__ = "0.1.0"
