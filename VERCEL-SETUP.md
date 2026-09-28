# Vercel setup

Project maintainer: Pranav Verma — pranavv829@gmail.com

## Submission blockers

The app can be imported as FastAPI, but its context, conversations and suppression
state currently live in process memory. Before using Vercel for judging, implement
shared persistent storage for all three. A successful health check alone does not
prove that context survives different function instances. Batch generation also
needs to meet the challenge's response deadline; increasing Vercel's execution
limit does not extend the judge's deadline.

## Import settings

1. Upload the clean source files to a GitHub repository, preserving folders.
2. In Vercel, choose Add New Project and import that repository.
3. Set Root Directory to the repository root (`./`), not `bot`.
4. Use the FastAPI framework preset. Keep build and output overrides unset.
5. The root `index.py` entry point exports `bot.main:app`, `.python-version` selects Python
   3.12, and `requirements.txt` supplies the dependencies.
6. Add environment variables for the production deployment:
   - `LLM_PROVIDER=gemini`
   - `GEMINI_MODEL=gemini-3.1-flash-lite`
   - `GEMINI_API_KEY` set privately in the Vercel dashboard.
7. Add shared-storage configuration after the storage integration is implemented.
8. Deploy and test `/v1/healthz`, `/v1/metadata`, context persistence, ticks and
   replies. The challenge must be able to access the production URL without a
   Vercel login or protection challenge.
9. Submit the production base URL only after persistence and timing checks pass.

Do not upload `.env` or place API keys in source files. The deployment is an API,
so the root page returns JSON; `/docs` is the interactive API documentation.

References:
- https://vercel.com/docs/frameworks/backend/fastapi
- https://vercel.com/docs/functions/runtimes/python
- https://vercel.com/kb/guide/vercel-services-fluid-compute
