"""Part of Speech To Text Streaming by Viprasol Tech Private Limited (https://viprasol.com).

Small helpers for generating deterministic synthetic PCM audio. These are used by the
examples and the offline test suite so that the streaming pipeline can be driven without
any real audio files or capture devices.
"""

from __future__ import annotations

import math
import struct


def tone_frame(samples: int, amplitude: int = 1000, period: int = 16) -> bytes:
    """Generate one deterministic frame of 16-bit PCM mono audio.

    Args:
        samples: Number of samples to generate.
        amplitude: Peak amplitude of the synthesized tone.
        period: Sample period of the tone in samples.

    Returns:
        Little-endian 16-bit PCM bytes of length ``samples * 2``.
    """
    if samples < 0:
        raise ValueError("samples must be non-negative")
    values = [
        int(amplitude * math.sin(2 * math.pi * (i % period) / period)) for i in range(samples)
    ]
    return struct.pack(f"<{samples}h", *values)


def silence(samples: int) -> bytes:
    """Generate ``samples`` of 16-bit PCM silence."""
    return tone_frame(samples, amplitude=0)
