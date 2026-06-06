"""Offline tests for the STT provider abstraction and the fake recognizer."""

from __future__ import annotations

import pytest

from speech_to_text_streaming.audio import tone_frame
from speech_to_text_streaming.providers import (
    FakeSTT,
    STTProvider,
    Transcript,
    load_provider,
)


def test_fake_is_a_provider() -> None:
    assert isinstance(FakeSTT(), STTProvider)
    assert FakeSTT().name == "fake"


def test_fake_emits_partial_after_one_word() -> None:
    stt = FakeSTT(samples_per_word=160)
    partial = stt.accept(tone_frame(160))
    assert partial is not None
    assert partial.is_final is False
    assert len(partial.text.split()) == 1


def test_fake_accumulates_words_across_chunks() -> None:
    stt = FakeSTT(samples_per_word=160)
    stt.accept(tone_frame(160))
    second = stt.accept(tone_frame(160))
    assert second is not None
    assert len(second.text.split()) == 2


def test_fake_buffers_partial_words() -> None:
    stt = FakeSTT(samples_per_word=160)
    # Fewer samples than one word -> no partial yet.
    assert stt.accept(tone_frame(80)) is None
    # Completing the word now yields a partial.
    assert stt.accept(tone_frame(80)) is not None


def test_fake_finalize_returns_final() -> None:
    stt = FakeSTT(samples_per_word=160)
    stt.accept(tone_frame(320))
    final = stt.finalize()
    assert isinstance(final, Transcript)
    assert final.is_final is True
    assert len(final.text.split()) == 2


def test_fake_is_deterministic() -> None:
    a = FakeSTT(samples_per_word=160)
    b = FakeSTT(samples_per_word=160)
    audio = tone_frame(480)
    a.accept(audio)
    b.accept(audio)
    assert a.finalize().text == b.finalize().text


def test_fake_reset_clears_state() -> None:
    stt = FakeSTT(samples_per_word=160)
    stt.accept(tone_frame(320))
    stt.reset()
    assert stt.finalize().text == ""


def test_fake_rejects_odd_length_chunk() -> None:
    with pytest.raises(ValueError, match="whole 16-bit samples"):
        FakeSTT().accept(b"\x00")


def test_invalid_samples_per_word() -> None:
    with pytest.raises(ValueError, match="positive"):
        FakeSTT(samples_per_word=0)


def test_load_provider_fake() -> None:
    assert load_provider("fake").name == "fake"
    assert load_provider("FAKE").name == "fake"


def test_load_provider_unknown() -> None:
    with pytest.raises(ValueError, match="unknown provider"):
        load_provider("does-not-exist")
