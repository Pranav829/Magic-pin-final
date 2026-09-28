# Vera Bot — Pranav Verma

Maintainer: **Pranav Verma**  
Contact: **pranavv829@gmail.com**

See the [main README](../README.md) for setup, API endpoints and checks.
The recommended Gemini entry point is `python run_local.py bot` from the
repository root. It loads the root `.env` and defaults to port 8081.

For direct Groq use, set `LLM_PROVIDER=groq` and `GROQ_API_KEY`, then run
`uvicorn bot.main:app --host 127.0.0.1 --port 8081` from the root.
Model selection uses `GEMINI_MODEL` or `GROQ_MODEL` according to the provider.

The composer combines category, merchant, trigger and optional customer data.
The context store supports versioned idempotent updates. Conversation tracking
handles repeated automated replies and explicit opt-outs before model calls.
State is in memory. Sequential model generation can exceed batch deadlines;
see the recorded [evaluation](../GEMINI-EVALUATION.md).
