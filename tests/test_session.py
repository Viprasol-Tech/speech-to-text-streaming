"""Offline tests for the streaming session manager."""

from __future__ import annotations

import pytest

from speech_to_text_streaming.audio import tone_frame
from speech_to_text_streaming.providers import FakeSTT
from speech_to_text_streaming.session import StreamingSession


def _session() -> StreamingSession:
    return StreamingSession(provider=FakeSTT(samples_per_word=160))


def test_session_tracks_stats() -> None:
    session = _session()
    session.push(tone_frame(160))
    session.push(tone_frame(160))
    assert session.stats.chunks == 2
    assert session.stats.bytes_in == 160 * 2 * 2
    assert session.stats.partials == 2


def test_session_close_returns_final() -> None:
    session = _session()
    session.push(tone_frame(320))
    final = session.close()
    assert final.is_final is True
    assert session.closed is True


def test_push_after_close_raises() -> None:
    session = _session()
    session.close()
    with pytest.raises(RuntimeError, match="closed session"):
        session.push(tone_frame(160))


def test_double_close_is_safe() -> None:
    session = _session()
    session.push(tone_frame(160))
    first = session.close()
    second = session.close()
    assert first.text == second.text
