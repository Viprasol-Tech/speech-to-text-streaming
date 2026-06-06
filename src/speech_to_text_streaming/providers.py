"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

STT provider abstraction plus a deterministic, fully offline fake recognizer and
lazily-imported adapters for ``faster-whisper`` and ``vosk``.

The audio "frame" model used across the project is intentionally simple: callers send
raw 16-bit little-endian PCM mono bytes. The :class:`FakeSTT` recognizer derives words
deterministically from the bytes so that the full streaming pipeline can be exercised
offline, with no network access, model downloads, or API keys.
"""

from __future__ import annotations

import importlib
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass

# A small, fixed vocabulary keeps fake transcripts deterministic and readable.
_VOCAB: tuple[str, ...] = (
    "hello",
    "world",
    "viprasol",
    "speech",
    "to",
    "text",
    "streaming",
    "realtime",
    "audio",
    "transcript",
    "partial",
    "final",
    "the",
    "quick",
    "brown",
    "fox",
)

# Number of PCM samples that map to a single fake word.
_SAMPLES_PER_WORD = 1600  # 0.1s of 16 kHz audio


@dataclass(frozen=True, slots=True)
class Transcript:
    """A single transcript event emitted by a provider.

    Attributes:
        text: The cumulative text recognized so far for this utterance.
        is_final: Whether this transcript is final (utterance complete).
    """

    text: str
    is_final: bool


class STTProvider(ABC):
    """Abstract base class for streaming speech-to-text providers.

    Providers are stateful per session: :meth:`accept` is fed successive audio
    chunks and returns the cumulative partial transcript so far (or ``None`` when a
    chunk yields no new text), and :meth:`finalize` flushes any buffered audio and
    returns the final transcript for the utterance.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider identifier."""

    @abstractmethod
    def accept(self, chunk: bytes) -> Transcript | None:
        """Accept a chunk of 16-bit PCM mono audio and return a partial transcript.

        Args:
            chunk: Raw little-endian 16-bit PCM mono audio bytes.

        Returns:
            A non-final :class:`Transcript` if new text became available, else ``None``.
        """

    @abstractmethod
    def finalize(self) -> Transcript:
        """Flush buffered audio and return the final transcript for the utterance."""

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state so the provider can handle a new utterance."""


class FakeSTT(STTProvider):
    """A deterministic, offline fake recognizer.

    Synthetic audio frames are mapped to words from a fixed vocabulary so that the
    end-to-end streaming pipeline can be tested without any external dependencies.
    The mapping is a pure function of the audio bytes, so identical input always
    produces identical transcripts.
    """

    def __init__(self, samples_per_word: int = _SAMPLES_PER_WORD) -> None:
        if samples_per_word <= 0:
            raise ValueError("samples_per_word must be positive")
        self._samples_per_word = samples_per_word
        self._words: list[str] = []
        self._pending = bytearray()

    @property
    def name(self) -> str:
        return "fake"

    def _drain(self) -> bool:
        """Convert whole buffered words into vocabulary tokens.

        Returns:
            ``True`` if at least one new word was produced.
        """
        bytes_per_word = self._samples_per_word * 2  # 2 bytes per 16-bit sample
        produced = False
        while len(self._pending) >= bytes_per_word:
            block = bytes(self._pending[:bytes_per_word])
            del self._pending[:bytes_per_word]
            samples = struct.unpack(f"<{self._samples_per_word}h", block)
            # Deterministic, bounded score from the sample magnitudes.
            score = sum(abs(s) for s in samples) % len(_VOCAB)
            self._words.append(_VOCAB[score])
            produced = True
        return produced

    def accept(self, chunk: bytes) -> Transcript | None:
        if len(chunk) % 2 != 0:
            raise ValueError("PCM chunk must contain whole 16-bit samples")
        self._pending.extend(chunk)
        if self._drain():
            return Transcript(text=" ".join(self._words), is_final=False)
        return None

    def finalize(self) -> Transcript:
        # Any trailing partial-word audio is dropped, matching real recognizers
        # that need a minimum amount of audio to emit a token.
        self._pending.clear()
        return Transcript(text=" ".join(self._words), is_final=True)

    def reset(self) -> None:
        self._words.clear()
        self._pending.clear()


class WhisperSTT(STTProvider):  # pragma: no cover - requires optional heavy dependency
    """Adapter around ``faster-whisper`` (imported lazily).

    This adapter buffers audio for the whole utterance and transcribes it on
    :meth:`finalize`. It is intentionally not exercised by the offline test suite.
    """

    def __init__(self, model_size: str = "base", sample_rate: int = 16000) -> None:
        self._sample_rate = sample_rate
        self._pending = bytearray()
        try:
            module = importlib.import_module("faster_whisper")
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed; install the 'whisper' extra"
            ) from exc
        self._model = module.WhisperModel(model_size)

    @property
    def name(self) -> str:
        return "faster-whisper"

    def accept(self, chunk: bytes) -> Transcript | None:
        self._pending.extend(chunk)
        return None

    def finalize(self) -> Transcript:
        import numpy as np

        pcm = np.frombuffer(bytes(self._pending), dtype="<i2").astype("float32") / 32768.0
        segments, _ = self._model.transcribe(pcm, language="en")
        text = " ".join(seg.text.strip() for seg in segments).strip()
        self._pending.clear()
        return Transcript(text=text, is_final=True)

    def reset(self) -> None:
        self._pending.clear()


class VoskSTT(STTProvider):  # pragma: no cover - requires optional heavy dependency
    """Adapter around ``vosk`` (imported lazily)."""

    def __init__(self, model_path: str, sample_rate: int = 16000) -> None:
        import json

        try:
            module = importlib.import_module("vosk")
        except ImportError as exc:
            raise RuntimeError("vosk is not installed; install the 'vosk' extra") from exc
        self._json = json
        self._model = module.Model(model_path)
        self._rec = module.KaldiRecognizer(self._model, sample_rate)

    @property
    def name(self) -> str:
        return "vosk"

    def accept(self, chunk: bytes) -> Transcript | None:
        if self._rec.AcceptWaveform(chunk):
            text = self._json.loads(self._rec.Result()).get("text", "")
            if text:
                return Transcript(text=text, is_final=False)
        return None

    def finalize(self) -> Transcript:
        text = self._json.loads(self._rec.FinalResult()).get("text", "")
        return Transcript(text=text, is_final=True)

    def reset(self) -> None:
        self._rec.Reset()


def load_provider(name: str, **kwargs: object) -> STTProvider:
    """Instantiate a provider by name.

    Args:
        name: One of ``"fake"``, ``"whisper"``/``"faster-whisper"``, or ``"vosk"``.
        **kwargs: Forwarded to the provider constructor.

    Returns:
        A configured :class:`STTProvider`.

    Raises:
        ValueError: If ``name`` is not a known provider.
    """
    key = name.lower()
    if key == "fake":
        return FakeSTT(**kwargs)  # type: ignore[arg-type]
    if key in {"whisper", "faster-whisper"}:
        return WhisperSTT(**kwargs)  # type: ignore[arg-type]
    if key == "vosk":
        return VoskSTT(**kwargs)  # type: ignore[arg-type]
    raise ValueError(f"unknown provider: {name!r}")
