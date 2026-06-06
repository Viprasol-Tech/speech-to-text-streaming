# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added

- FastAPI WebSocket endpoint `/ws/transcribe` emitting partial and final transcripts.
- `STTProvider` abstract base class and a deterministic offline `FakeSTT` recognizer.
- Optional lazily-imported `faster-whisper` and `vosk` adapters.
- `StreamingSession` manager with per-utterance lifecycle and statistics.
- `/health` route reporting status, version, and active provider.
- Synthetic audio helpers, an offline demo, and an offline test suite.
- Tooling: ruff, mypy strict, pytest, multi-OS CI, Docker, and docs.

[0.1.0]: https://github.com/Viprasol-Tech/speech-to-text-streaming/releases/tag/v0.1.0
