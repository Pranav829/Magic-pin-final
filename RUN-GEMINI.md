# Run locally with Gemini

The provider adapter preserves the bot's original prompts and composition logic.
The original judge simulator is unchanged. `run_local.py` configures it and saves
individual message scores as JSON.

Use Python from `.venv/Scripts/python.exe`. Dependencies are installed from
`bot/requirements.txt`. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`, or supply it through
your environment. No other project or machine-specific path is required.
Keys are never embedded in source files or result files.

Start the bot:

```powershell
& ./.venv/Scripts/python.exe run_local.py bot
```

Open http://127.0.0.1:8081/docs . In another terminal, run the original evaluation:

```powershell
$env:PYTHONIOENCODING='utf-8'
& ./.venv/Scripts/python.exe run_local.py judge full_evaluation
```

Restart the bot before each evaluation because trigger suppression is held in
memory. For the conversational scenarios, use `judge all` instead.

For a separately labeled quality diagnostic, set `$env:QUALITY_ONLY='1'` in the
judge terminal. This allows 120 seconds per tick instead of the original 15;
it must not be interpreted as passing the original timing test. Set
`$env:LOCAL_PORT='8082'` in both terminals to use a separate instance.

The score is an LLM rubric assessment, not a statistical accuracy estimate.
The runner also prints the arithmetic mean because the original judge floors
each dimension average before adding them. The original scenario success flag
is permissive and can report success despite failed checks or timed-out batches.
