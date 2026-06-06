"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

Offline demo: drive the fake recognizer through a :class:`StreamingSession` with
synthetic audio and print the partial and final transcripts. Runs with no network,
models, or API keys.

Usage::

    python examples/stream_demo.py
"""

from __future__ import annotations

from speech_to_text_streaming.audio import tone_frame
from speech_to_text_streaming.providers import FakeSTT
from speech_to_text_streaming.session import StreamingSession


def main() -> None:
    session = StreamingSession(provider=FakeSTT())
    for i in range(5):
        partial = session.push(tone_frame(1600, amplitude=500 + i * 250))
        if partial is not None:
            print(f"partial: {partial.text}")
    final = session.close()
    print(f"final:   {final.text}")
    print(f"stats:   {session.stats}")


if __name__ == "__main__":
    main()
