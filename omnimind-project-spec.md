# OmniMind — Multilingual Meeting Intelligence, Document Voice & Universal Translator Platform

> One pipeline. Any language in, any language out — whether it's a live meeting, a document, or a conversation — with an audit trail enterprises can trust.

---

## 1. Problem Statement

Global and Indian enterprises lose critical decisions in three recurring ways:

1. **Meetings are lossy.** Decisions, owners, and deadlines discussed verbally rarely make it into a trackable system. This is worse in multilingual/code-switched settings (e.g., Hindi-English "Hinglish") that Western tools (Otter, Fireflies, Gong) are not tuned for.
2. **Documents are locked to one language and one modality (text).** A French compliance PDF can't be consumed by a Japanese-speaking or visually impaired employee without manual translation/narration.
3. **Cross-language conversation is friction-heavy.** Real-time or async communication between speakers of different languages still relies on human interpreters or clunky, literal machine translation that loses business/legal nuance.

Regulated industries (BFSI, legal, compliance-heavy MNCs) additionally need **provenance** — a verifiable, timestamped record of who said what, when, and what was decided — something no current meeting tool provides well.

---

## 2. Product Scope — Three Modes, One Core Pipeline

| Mode | Input | Output | Core Value |
|---|---|---|---|
| **Meeting Intelligence** | Multi-speaker audio (any language/mixed) | Diarized transcript, decisions, action items, owners, deadlines, risks, provenance log | Turns meetings into tracked execution |
| **Document Intelligence** | PDF/DOCX/scanned image, any language | Translated/simplified text + chaptered audio narration in target language | Makes documents accessible across languages & literacy modes |
| **Universal Translator** | Live or recorded speech, source language | Speech/text in target language (optionally voice-cloned) | Removes language barriers in real conversation |

All three modes share one core pipeline (ASR → embedding → reasoning → TTS), avoiding duplicated engineering.

---

## 3. Shared Core Pipeline

```
Audio / Document Input
        │
        ▼
┌─────────────────────┐
│  Ingestion Layer     │  (audio cleanup, OCR for docs, VAD)
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  Whisper large-v3-turbo │  ASR — auto language detection, ~99 languages
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  pyannote.audio       │  Speaker diarization (meetings only)
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  BGE-M3 / E5-multilingual │  Multilingual embeddings — single vector space across 100+ languages
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  Qwen2.5 (32B/72B-Instruct) │  Reasoning: summarize, translate, extract decisions/actions, simplify
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  LangGraph Agent Layer │  Ticket creation, notifications, escalation, compliance logging
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│  XTTS-v2 / MMS-TTS     │  Text-to-speech in target language (voice cloning optional)
└─────────────────────┘
```

### Model Choices & Rationale

| Component | Model | Why |
|---|---|---|
| ASR | `openai/whisper-large-v3-turbo` | Best accuracy/speed tradeoff on HF, strong multilingual + code-switch handling |
| Diarization | `pyannote/speaker-diarization-3.1` | Industry-standard, HF-hosted, good with 2–10 speakers |
| VAD | `snakers4/silero-vad` | Fast, accurate segment boundaries pre-Whisper |
| Embeddings | `BAAI/bge-m3` | Single embedding space across 100+ languages — enables cross-lingual search |
| Reasoning/Translation | `Qwen/Qwen2.5-32B-Instruct` (or 72B if resources allow) | Strong multilingual reasoning, better at nuanced business/legal translation than literal MT models |
| OCR (scanned docs) | `Tesseract` (Latin scripts) / `doctr` (non-Latin: Hindi, Japanese, Arabic) | Script coverage for non-Latin languages |
| TTS | `coqui/XTTS-v2` (17 languages, voice cloning) + `facebook/mms-tts` (1100+ languages, fallback) | Coverage + quality where it matters most |

---

## 4. Feature Breakdown

### 4.1 Meeting Intelligence
- Upload audio (up to multi-hour meetings)
- Auto language detection **per speaker** (not just per file — real meetings mix languages by person)
- Diarized transcript (Speaker A/B/C…)
- LLM extraction:
  - Topics discussed
  - Decisions made
  - Action items → owner → deadline (structured table)
  - Risks / unresolved questions flagged
- **Decision provenance log**: every decision timestamped, linked to audio clip, exportable as signed PDF — built for compliance/audit use in BFSI
- Execution integration: auto-create Jira tickets / GitHub issues / Slack DMs to owners
- Follow-up agent: cron-based check on task status, auto-escalation on missed deadlines

### 4.2 Document Intelligence
- Upload PDF/DOCX/scanned image in any language
- OCR + structure-preserving extraction (headings, tables kept intact)
- On-demand: summarize, simplify (reading-level adjustable), or translate to selected language
- Chaptered TTS narration matching document structure
- **Accessibility mode**: screen-reader-grade narration for visually impaired users in their native language

### 4.3 Universal Translator
- User selects source + target language (or auto-detect source)
- Modes:
  - **Async**: record voice memo → get back audio + side-by-side text in target language
  - **Live/near-real-time**: conversation mode between two speakers, each hearing the other's speech translated
- Optional voice cloning so translated speech retains speaker's vocal identity
- **Glossary lock**: org-defined terms that must never be translated (e.g., "Trading Mandate" stays "Trading Mandate") — critical for enterprise trust

### 4.4 Cross-Lingual Knowledge Search
- Query in any language, retrieve answers from meetings/documents stored in any other language
- Powered by BGE-M3's shared multilingual embedding space — no need to translate before search

---

## 5. Target Languages (Launch Scope)

Prioritize by buyer relevance, not maximum coverage:

**Tier 1 (full tuning + voice cloning):** Hindi, English, Japanese, French, Spanish
**Tier 2 (Whisper/Qwen native support, lighter tuning):** Mandarin, German, Arabic, Portuguese
**Tier 3 (fallback via MMS-TTS, no cloning):** any of Whisper's ~99 supported languages

---

## 6. Architecture — Repo Structure

```
omnimind/
├── core/
│   ├── ingestion/          # audio cleanup, VAD, OCR
│   ├── asr/                # Whisper wrapper, language detection
│   ├── diarization/        # pyannote wrapper
│   ├── embeddings/         # BGE-M3 wrapper, vector store interface
│   ├── reasoning/          # Qwen prompts: extraction, translation, simplification
│   ├── tts/                # XTTS-v2 + MMS-TTS wrappers, voice cloning
│   └── pipeline.py         # orchestrates shared core pipeline
│
├── modes/
│   ├── meeting_intelligence/
│   │   ├── extractor.py    # decisions, action items, risks
│   │   ├── provenance.py   # timestamped decision log, PDF export
│   │   └── agents/         # ticket creation, notification, escalation (LangGraph)
│   ├── document_intelligence/
│   │   ├── ocr.py
│   │   ├── structure.py    # heading/table preservation
│   │   └── narrator.py     # chaptered TTS output
│   └── translator/
│       ├── async_mode.py
│       ├── live_mode.py
│       └── glossary.py     # locked-term enforcement
│
├── integrations/
│   ├── jira.py
│   ├── github.py
│   └── slack.py
│
├── storage/
│   ├── vector_store/       # FAISS / pgvector for BGE-M3 embeddings
│   └── audit_log/          # immutable provenance records
│
├── api/
│   └── main.py              # FastAPI entrypoint
│
├── tests/
├── requirements.txt
└── README.md
```

---

## 7. MVP Build Order (buildable incrementally)

1. **Core ASR + diarization pipeline** — upload audio, get diarized multilingual transcript (this alone, done well for Hinglish + one other language, is already differentiated)
2. **Qwen-based extraction** — decisions/action-items/owner/deadline table from transcript
3. **One execution integration** — pick Jira *or* Slack, do it well, don't split focus across three
4. **Provenance log** — timestamped decision → audio clip link → exportable report
5. **Document Intelligence mode** — OCR + translate + TTS narration for one non-English language
6. **Universal Translator (async mode first)** — record → translated audio + text; live mode later
7. **Cross-lingual search** — BGE-M3 vector store over stored meetings/documents
8. **Glossary lock + voice cloning** — polish features once core loop is trusted

---

## 8. UI — Built Separately

The frontend is being designed and built as a standalone project, not inside this repo. The backend (`api/main.py`) must expose a clean REST/WebSocket API so the UI can be developed and swapped independently.

**API surface the UI depends on:**

| Endpoint (indicative) | Purpose |
|---|---|
| `POST /meetings/upload` | Upload audio, kick off pipeline |
| `GET /meetings/{id}/transcript` | Diarized transcript + speaker labels |
| `GET /meetings/{id}/summary` | Decisions, action items, risks, owners/deadlines |
| `GET /meetings/{id}/provenance` | Timestamped decision log, exportable PDF |
| `POST /documents/upload` | Upload doc, choose target language |
| `GET /documents/{id}/audio` | Chaptered TTS narration output |
| `POST /translate/async` | Upload/record audio, get translated audio + text |
| `WS /translate/live` | Live speech-to-speech translation stream |
| `GET /search` | Cross-lingual query over stored meetings/documents |

Keep all endpoints language-agnostic (accept a `target_lang` param) so the UI's language selector maps directly to the API without backend changes.

---

## 9. Why This Differentiates from Existing Tools

- **Hinglish/code-switch tuning**: no major competitor (Otter, Fireflies, Gong, Fathom) optimizes for this — genuine technical moat
- **Provenance, not just notes**: audit-grade decision logging solves a *mandated* compliance pain, not a nice-to-have
- **One pipeline, three products**: meeting, document, and translator modes share engineering instead of being three separate builds
- **Nuance-aware translation**: Qwen-based translation captures business/legal intent better than literal MT models (NLLB, M2M100) for this use case
- **Accessibility angle**: native-language document narration is a genuine underserved need with social-good framing, useful for CSR/grant narratives if pitched beyond pure commercial

---

## 10. Open Questions to Resolve Before Building

- [ ] Which 2–3 languages beyond Hindi/English to launch with (recommend: Japanese, French — validate against target buyer)
- [ ] Self-hosted vs. hosted-inference for Qwen (32B is heavy — consider quantized GGUF or hosted endpoint for MVP)
- [ ] Live translation mode latency budget (near-real-time vs. true real-time — affects model/infra choice significantly)
- [ ] Data residency / compliance requirements if targeting BFSI (audio storage location, retention policy)
