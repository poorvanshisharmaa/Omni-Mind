# OmniMind Backend

A working FastAPI implementation of the API surface described in
[`omnimind-project-spec.md`](../omnimind-project-spec.md):
Meeting Intelligence, Document Intelligence, Universal Translator, and
cross-lingual search — all backed by a real SQLite database, real file
handling, and real background job processing.

## What's real vs. mocked

This machine has no GPU, no HuggingFace token for gated models (pyannote),
and no LLM API key. Rather than half-implement the spec's ML stack
(Whisper, pyannote, BGE-M3, Qwen2.5, XTTS-v2), every heavy model sits
behind a small interface (`ASREngine`, `ReasoningEngine`, `TranslationEngine`,
`TTSEngine` in `app/core/`) with a working implementation on the other side:

| Stage | Spec model | What actually runs here |
|---|---|---|
| ASR | Whisper large-v3-turbo | `MockASREngine` — deterministic, template-based transcript (seeded from the file, so re-uploading the same audio gives the same transcript) |
| Diarization | pyannote.audio | Round-robin speaker assignment |
| Reasoning (decisions/action items/risks) | Qwen2.5 | `RuleBasedReasoningEngine` — real regex/keyword extraction over whatever transcript text it's given |
| Translation | Qwen2.5 / NLLB | `LexiconTranslationEngine` — real word-level dictionary substitution (en→hi/fr/es/ja), glossary-lock aware |
| TTS | XTTS-v2 / MMS-TTS | `SystemSayTTSEngine` — **real speech synthesis** via macOS's built-in `say` + `afconvert` (falls back to a valid silent WAV on non-macOS) |
| Document text extraction | — | **Real** — `pypdf` / `python-docx` / plain text, not mocked |
| Cross-lingual search | BGE-M3 embeddings | **Real** TF-IDF ranking over ingested meetings/documents (lexical, not semantic — see `app/storage/vector_store.py`) |
| Jira/GitHub/Slack integrations | — | **Real** HTTP clients, active if you set credentials in `.env`, otherwise a labeled no-op |

Every mock is a small, swappable class — replacing `MockASREngine` with a
real `faster-whisper` wrapper, for example, is a one-file change; nothing
else in the pipeline needs to know.

You can also skip the mock ASR entirely: pass `sample_transcript` as a form
field on `POST /meetings/upload` to feed the reasoning engine real text
directly and see the extraction logic run on it.

## Setup

Requires Python 3.11+.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want to wire up Jira/GitHub/Slack —
otherwise the defaults work with zero configuration.

## Run

```sh
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs
Health check: http://localhost:8000/health

Uploaded files, generated audio, exported PDFs, and the SQLite database all
live under `data/` (gitignored, created automatically on first run).

## Test

```sh
pytest
```

9 tests cover meeting upload → transcript → extraction → provenance PDF,
document upload → translation → narration, glossary-locked translation,
the live-translate WebSocket, and cross-lingual search — all exercised
against the real pipeline, not mocked at the test layer.

## API

| Endpoint | Purpose |
|---|---|
| `POST /meetings/upload` | Upload audio (`file`, optional `language`, optional `sample_transcript`) |
| `GET /meetings` / `GET /meetings/{id}` | List / status |
| `GET /meetings/{id}/transcript` | Diarized transcript |
| `GET /meetings/{id}/summary` | Decisions, action items, risks |
| `GET /meetings/{id}/provenance` | Timestamped decision log |
| `GET /meetings/{id}/provenance/export.pdf` | Provenance log as a real PDF |
| `POST /documents/upload` | Upload PDF/DOCX/TXT/MD (`file`, `target_lang`, optional `source_lang`) |
| `GET /documents` / `GET /documents/{id}` | List / original vs. translated chapters |
| `GET /documents/{id}/audio` | Chaptered narration audio URLs |
| `POST /translate/async` | Translate `text` or an uploaded `audio` file |
| `WS /translate/live` | Streaming translation over a WebSocket |
| `POST/GET/DELETE /translate/glossary` | Manage locked terms |
| `GET /search?q=...` | Cross-lingual-ish search over everything ingested |

## Repo layout

Follows the structure in the product spec:

```
app/
├── core/            # ASR, diarization, reasoning, translation, TTS, ingestion, pipeline orchestration
├── modes/           # meeting_intelligence / document_intelligence / translator
├── integrations/    # jira, github, slack
├── storage/         # file paths, search index, provenance log
├── routers/         # FastAPI route handlers
├── models.py        # SQLModel tables
├── db.py, config.py, main.py
tests/
```
