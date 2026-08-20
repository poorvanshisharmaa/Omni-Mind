# OmniMind

OmniMind — a multilingual meeting intelligence and translation platform for enterprise/BFSI users. This repo holds both the frontend and the backend. See [`omnimind-project-spec.md`](./omnimind-project-spec.md) for the full product spec and architecture.

Three main modes, accessible via a sidebar:

- **Meeting Intelligence** — upload audio, get a diarized transcript, decisions/action items/risks, and a provenance log with audio-linked, exportable timestamps.
- **Document Intelligence** — upload a PDF/DOCX, pick a language pair, and get a side-by-side original-vs-translated view plus chaptered audio narration.
- **Universal Translator** — two-column live/async conversation view with per-side language selectors, mic recording, waveform visualization, and inline translated text/audio.

Global: cross-lingual search in the top nav, dark/light mode toggle, and a calm, enterprise-grade aesthetic (think Linear or Notion, not a consumer app).

## Design

Color palette:

| Token | Hex | RGB |
|---|---|---|
| Primary | `#464B71` | `rgb(70, 75, 113)` |
| Accent | `#118AB2` | `rgb(17, 138, 178)` |
| Support | `#7CD5C7` | `rgb(124, 213, 199)` |
| Background | `#F2F2ED` | `rgb(242, 242, 237)` |

## Repo layout

```
.
├── src/, public/, ...   # frontend (this directory's root)
├── backend/              # FastAPI backend — see backend/README.md
└── omnimind-project-spec.md
```

## Frontend

TanStack Start (React 19 + TanStack Router/Query), Tailwind CSS v4, and shadcn/radix UI primitives. Deploys as a Cloudflare Worker via Nitro.

Requires [Bun](https://bun.sh).

```sh
git clone <this-repository-url>
cd intel-fluent-sync
bun install
bun run dev
```

Other scripts: `bun run build`, `bun run preview`, `bun run lint`, `bun run format`.

## Backend

FastAPI + SQLite, implementing the Meeting Intelligence / Document Intelligence / Universal Translator / search API the frontend talks to. Full details, including what's real vs. mocked in the ML pipeline, are in [`backend/README.md`](./backend/README.md).

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`. Run `pytest` from `backend/` for the test suite.
