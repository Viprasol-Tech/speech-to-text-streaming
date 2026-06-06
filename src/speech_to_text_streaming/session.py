"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

The :class:`StreamingSession` drives a single client utterance: it feeds audio chunks
to an :class:`~speech_to_text_streaming.providers.STTProvider` and yields partial and
final transcript events. It is transport-agnostic so it can be reused outside of the
WebSocket endpoint (for example in tests or batch tooling).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from speech_to_text_streaming.providers import STTProvider, Transcript


@dataclass(slots=True)
class SessionStats:
    """Counters describing a streaming session's lifetime."""

    chunks: int = 0
    bytes_in: int = 0
    partials: int = 0


@dataclass(slots=True)
class StreamingSession:
    """Manage the transcription lifecycle for one utterance.

    Args:
        provider: The STT backend used to recognize audio.
    """

    provider: STTProvider
    stats: SessionStats = field(default_factory=SessionStats)
    _closed: bool = False

    def push(self, chunk: bytes) -> Transcript | None:
        """Feed a chunk of audio and optionally get a partial transcript.

        Args:
            chunk: Raw little-endian 16-bit PCM mono audio bytes.

        Returns:
            A non-final :class:`Transcript` if new text became available, else ``None``.

        Raises:
            RuntimeError: If the session has already been closed.
        """
        if self._closed:
            raise RuntimeError("cannot push to a closed session")
        self.stats.chunks += 1
        self.stats.bytes_in += len(chunk)
        result = self.provider.accept(chunk)
        if result is not None:
            self.stats.partials += 1
        return result

    def close(self) -> Transcript:
        """Finalize the utterance and return the final transcript.

        Returns:
            The final :class:`Transcript`. Closing twice returns the same final result.
        """
        if self._closed:
            return self.provider.finalize()
        self._closed = True
        return self.provider.finalize()

    @property
    def closed(self) -> bool:
        """Whether :meth:`close` has been called."""
        return self._closed
