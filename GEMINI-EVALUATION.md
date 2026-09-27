# Gemini evaluation — 27 September 2026

Historical evaluation before repository-readiness fixes. Duplicate-context
acceptance and HTTP error statuses have since been corrected and covered by
offline regression checks. The quality evaluation has not been rerun.
Detailed transcripts and logs referenced below are local, Git-ignored artifacts.

Bot and judge: `gemini-3.1-flash-lite`. Dataset: 5 categories, 10 merchants,
25 triggers. This is the repository's Python judge simulator, not Jest.

## Original timing test

All five batches timed out at the simulator's unchanged 15-second deadline.
No messages were returned to the judge in time, so no valid baseline quality
percentage exists. The simulator nevertheless exits successfully because its
full-evaluation function ignores tick failures when choosing its return value.
See `judge-full.log` and `bot.stderr.log`.

## Separate quality diagnostic

On a fresh bot instance, the tick wait was extended to 120 seconds solely to
measure message quality. Prompts, scoring rubric, batch size and bot behavior
were preserved. This is not a successful run under the original deadline.

- Messages scored: 25 of 25.
- Arithmetic mean: **39.40/50 (78.80%)**.
- Original judge's displayed score: **36/50 (72%)**. It floors each dimension's
  average before adding them.
- Judge fallback scores: 0.
- Logged bot composition failures: 0.
- Batch times: 43.680, 15.934, 16.623, 30.028, 29.292 seconds.
- All five exceeded the simulator's 15-second deadline; two exceeded the
  challenge brief's 30-second deadline.

| Dimension | Mean / 10 |
|---|---:|
| Specificity | 8.76 |
| Category fit | 8.24 |
| Merchant fit | 7.72 |
| Decision quality | 6.96 |
| Engagement | 7.72 |

Detailed messages and judge rationales are in
`judge-full_evaluation-quality-only-results.json`; console output is in
`judge-quality.log`. These are LLM rubric judgments from one run, not measured
classification accuracy or an official competition score. Both bot and judge
use the same model. The stock full-evaluation harness does not push customer
contexts, so customer-trigger results reflect that harness limitation.

## Conversation and contract findings

- Auto-replies: wait on turns 1 and 2; end on turn 3.
- Hostile opt-out: graceful apology; code suppresses subsequent merchant sends.
- Commitment transition: simulator reported “Response unclear” but still marked
  the scenario passed. This is inconclusive rather than a verified pass.
- Reposting identical contexts returned failures. The store treats equal versions
  as stale instead of accepting an idempotent no-op.
- Scenario warmup likewise reports success despite individual context failures.
- Python compilation checks passed.

The largest operational issue is sequential synchronous LLM calls inside the
tick handler. The lowest-scoring diagnostic messages were the festival trigger
(28/50), kids-yoga follow-up (32/50), and compliance trigger (34/50). Review their
stored rationales for timing relevance and factual-grounding concerns.

## Running again

The bot was started at http://127.0.0.1:8081/docs and the isolated quality instance
at http://127.0.0.1:8082/docs. Restart with fresh in-memory state before rescoring.
See `RUN-GEMINI.md` for commands. Changes add Gemini configuration, accurate model
metadata, and a result-saving runner; the original judge source is unchanged.
No secret values were written to the project.
