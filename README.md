<p align="center"><img src="docs/assets/logo.png" width="120"></p>

# Speech To Text Streaming

> Realtime speech-to-text streaming over a single FastAPI WebSocket — partial and final transcripts, a pluggable recognizer, and a fully offline fake so you can build and test without keys.

*Built and maintained by [Viprasol Tech](https://viprasol.com) — Fintech Experts. Full-Stack Builders.*

[![CI](https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/speech-to-text-streaming/ci.yml?branch=main&style=flat-square)](https://github.com/Viprasol-Tech/speech-to-text-streaming/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![Telegram](https://img.shields.io/badge/Telegram-help-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/viprasol_help)
[![Stars](https://img.shields.io/github/stars/Viprasol-Tech/speech-to-text-streaming?style=flat-square)](https://github.com/Viprasol-Tech/speech-to-text-streaming/stargazers)

## ✨ Features

- 🎙️ **Realtime WebSocket streaming** — push raw PCM audio chunks, receive transcripts as you go.
- ⚡ **Partial + final transcripts** — low-latency interim results, then a clean final.
- 🧩 **Pluggable provider ABC** — swap recognizers behind one clean interface.
- 🧪 **Deterministic offline fake** — exercise the whole pipeline with zero network, models, or keys.
- 🔌 **Lazy adapters** — optional `faster-whisper` and `vosk` backends, imported only when used.
- 🩺 **/health endpoint** — readiness and version reporting out of the box.
- 📊 **Session manager** — per-utterance lifecycle with byte/chunk/partial stats.
- 🐳 **Docker-first** — `docker compose up` and you are streaming.
- 🧰 **Typed end to end** — `py.typed`, `mypy --strict` clean.
- ✅ **Heavily tested** — offline tests via the FastAPI WebSocket `TestClient`.
- 🎯 **Strict tooling** — ruff lint + format, mypy strict, pytest, multi-OS CI.
- 📦 **Single-source config** — one `pyproject.toml` for deps, lint, types, and tests.

## 🚀 Quickstart

### Docker (recommended)

```bash
docker compose up --build
# server on http://localhost:8000  (health: /health, websocket: /ws/transcribe)
```

### Local

```bash
pip install -e ".[dev]"
stt-server            # or: uvicorn speech_to_text_streaming.app:app --reload
```

## 🧑‍💻 Usage

Connect to `ws://localhost:8000/ws/transcribe`, send **binary** little-endian 16-bit PCM
mono chunks, then the **text** message `__end__` to finish. The server replies with JSON
`{"type": "partial"|"final", "text": "..."}`.

```python
from speech_to_text_streaming.audio import tone_frame
from speech_to_text_streaming.providers import FakeSTT
from speech_to_text_streaming.session import StreamingSession

session = StreamingSession(provider=FakeSTT())
for _ in range(5):
    partial = session.push(tone_frame(1600))
    if partial:
        print("partial:", partial.text)
print("final:", session.close().text)
```

Run the offline demo: `python examples/stream_demo.py`.

## 🗺️ Roadmap

- [x] WebSocket streaming with partial + final transcripts
- [x] Provider ABC + deterministic offline fake
- [x] Optional faster-whisper / vosk adapters
- [ ] Voice activity detection (VAD) based endpointing
- [ ] Word-level timestamps
- [ ] Multi-language model selection

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

## 📬 Contact — Viprasol Tech Private Limited

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, algorithmic trading systems, MT4/MT5 bots, AI voice agents, and B2B SaaS. Need a custom build? [Get in touch](mailto:support@viprasol.com).*

## 📄 License

Released under the [MIT License](LICENSE) — © 2025 Viprasol Tech Private Limited.
