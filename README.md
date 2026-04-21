# Promo Machine

An end-to-end AI pipeline that takes a reference video (a competitor's ad, a trending reel, a product demo) and spits out ready-to-publish promotional content: analysed patterns, generated scripts / hooks / captions, TTS voiceover, and a rendered short-form video.

> 🧪 **Status:** personal experiment · **Stack:** FastAPI + React 19 + OpenAI GPT-4o / GPT-4o Vision

---

## What it does

You point Promo Machine at a source video (URL or upload). It:

1. **Downloads** the video (`yt-dlp` under the hood, supports YouTube / Instagram / TikTok).
2. **Analyses** it visually: extracts keyframes, detects visual patterns (cuts, motion, on-screen text, composition) using **GPT-4o Vision**.
3. **Generates copy** in the style you ask for: hooks, voiceover scripts, captions / descriptions — all via GPT-4o with tuned prompts per content type.
4. **Synthesises voice** via Microsoft Edge TTS (multiple voices / languages), **mixes** with trending background audio.
5. **Renders** a new short-form vertical video (`moviepy`) with device-frame mockups, on-screen text, transitions, and your new voiceover.

Everything is stored per-project in a local SQLite DB.

## Architecture

```
backend/
├── app.py              # FastAPI app entry
├── routes/             # HTTP endpoints
│   ├── projects.py     #   CRUD for projects
│   ├── analyze.py      #   kick off analysis pipeline
│   ├── generate.py     #   kick off content generation
│   └── audio.py        #   TTS + mixer endpoints
├── scanner/
│   └── downloader.py   # yt-dlp wrapper
├── analyzer/
│   ├── frame_extractor.py      # video → keyframes
│   ├── pattern_detector.py     # GPT-4o Vision prompting
│   └── video_analyzer.py       # orchestrates frames + patterns
├── generator/
│   ├── prompts.py      # system + style prompts
│   ├── hook_writer.py  # short attention hooks
│   ├── script_writer.py# voiceover scripts
│   └── copy_writer.py  # captions / descriptions
├── audio/
│   ├── tts.py          # Edge TTS synthesis
│   ├── trending.py     # trending / royalty-free tracks lookup
│   └── mixer.py        # pydub mixing (voice + music)
├── renderer/
│   ├── composer.py     # moviepy composition
│   ├── device_frame.py # iPhone / Android mockups
│   ├── effects.py      # transitions, text overlays
│   └── batch.py        # queue + progress
└── db/
    ├── models.py       # SQLAlchemy + SQLite
    └── database.py

frontend/                # React 19 + Vite 8 + TypeScript 6
  src/                   # tabs: Projects / Scan / Analyze / Generate / Render
```

## Tech stack

| Area | Stack |
|---|---|
| Backend | **FastAPI**, **SQLite** (aiosqlite), **Pydantic** |
| AI | **OpenAI GPT-4o**, **GPT-4o Vision** |
| Video | **yt-dlp**, **moviepy**, **Pillow** |
| Audio | **Microsoft Edge TTS**, **pydub** |
| Frontend | **React 19**, **Vite 8**, **TypeScript 6** |
| Language | Python 3.12+ |

## Running locally

```bash
# 1. Configure
cp config.example.yaml config.yaml
# edit config.yaml: openai_api_key, data_dir, etc.

# 2. Install Python deps
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Install frontend deps
cd frontend && npm install && npm run build && cd ..

# 4. Run
python main.py
# FastAPI starts on http://127.0.0.1:8000
# Browser auto-opens after 2s
```

Minimum `config.yaml`:

```yaml
openai_api_key: "sk-..."
data_dir: "./data"
downloads_dir: "./data/downloads"
projects_dir: "./data/projects"
db_path: "./data/promo.db"
host: "127.0.0.1"
port: 8000
frontend_port: 5173
```

## Why this project exists

Three reasons:

1. **Hands-on with the 2026 AI stack.** GPT-4o Vision, Edge TTS, structured prompting, agent-style pipelines — this project touches all of them in one place. You learn real constraints (token limits, streaming, cost, latency) only when you build something end-to-end.
2. **Video is where Python shines.** `moviepy` + `pydub` + `yt-dlp` give you an absurd amount of leverage in a hundred lines of code. Wanted to feel that again.
3. **Scratching my own itch.** Analyzing competitor short-form content manually is tedious; the AI can't replace judgment, but it can absolutely draft the first five variants of a hook faster than I can.

## Caveats & license

- Personal / non-commercial project. Not for production.
- OpenAI and Edge TTS usage policies apply to whatever content you generate.
- Respect platform ToS when downloading videos (YouTube / Instagram / TikTok).
- MIT — see LICENSE (if attached) or treat as MIT.
