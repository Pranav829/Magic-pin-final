# Vera Bot — Pranav Verma

A WhatsApp-style merchant engagement assistant for the magicpin AI Challenge.

**Project maintainer:** Pranav Verma  
**Contact:** pranavv829@gmail.com

Vera combines category, merchant, trigger, and optional customer context to
compose messages. It includes an in-memory context store, conversation tracking,
rule-based opt-out and auto-reply handling, and Gemini or Groq composition.

## Quick start

Requires Python 3.12. From the repository root:

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r bot/requirements.txt
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, then run:

```powershell
& ./.venv/Scripts/python.exe run_local.py bot
```

On macOS/Linux, use `.venv/bin/python` instead and `cp .env.example .env`.
Open http://127.0.0.1:8081/docs for the interactive API documentation.
Local keys, logs, evaluation transcripts and virtual environments are ignored by Git.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/v1/healthz` | Health and context counts |
| GET | `/v1/metadata` | Project identity and configured model |
| POST | `/v1/context` | Versioned context updates |
| POST | `/v1/tick` | Proactive message generation |
| POST | `/v1/reply` | Conversation replies |

Equal context versions are accepted without replacing the stored payload.
Older versions return HTTP 409; invalid scopes return HTTP 400.

## Checks and evaluation

Offline checks require no API keys:

```powershell
& ./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

With a fresh running bot, the supplied judge simulator can call Gemini:

```powershell
& ./.venv/Scripts/python.exe run_local.py judge full_evaluation
```

See [Gemini setup](RUN-GEMINI.md), [evaluation findings](GEMINI-EVALUATION.md),
and [upload readiness](REPOSITORY-READINESS.md). GitHub Actions runs offline
checks on pushes and pull requests.

## Design and current limits

- Four context dimensions ground messages in the supplied synthetic fixtures.
- Rules intercept hostile replies and repeated automated replies.
- Conversation and suppression state lives in memory and resets on restart.
- Composition uses synchronous, sequential model calls; batches can exceed the
  judge deadline. This remains an identified performance limitation.
- The historical quality-only diagnostic averaged 78.8% across 25 messages with
  extended waits. All five batches timed out in the original timing test; the
  quality figure is not an official score or a timing-compliant pass.

The challenge briefs, seed fixtures and supplied judge are reference materials
from the magicpin AI Challenge. Their source attribution is retained.
# Magic-pin-final
