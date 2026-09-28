"""Run the Gemini bot or original judge, saving evaluation evidence."""
import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import asdict
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
load_dotenv(ROOT / 'bot' / '.env')
parser = argparse.ArgumentParser(description='Run the Gemini bot or challenge judge.')
parser.add_argument('command', choices=['bot', 'judge'])
parser.add_argument('scenario', nargs='?', default='full_evaluation', choices=['warmup', 'phase2_short', 'auto_reply_hell', 'intent_transition', 'hostile', 'all', 'full_evaluation'])
args = parser.parse_args()
if not os.getenv('GEMINI_API_KEY'):
    parser.error('Set GEMINI_API_KEY in your environment or copy .env.example to .env and fill it in.')
os.environ['LLM_PROVIDER'] = 'gemini'
os.environ.setdefault('GEMINI_MODEL', 'gemini-3.1-flash-lite')

if args.command == 'bot':
    import uvicorn
    uvicorn.run('bot.main:app', host='127.0.0.1', port=int(os.getenv('LOCAL_PORT', '8081')))
else:
    import judge_simulator as j
    j.BOT_URL = 'http://127.0.0.1:' + os.getenv('LOCAL_PORT', '8081')
    j.LLM_PROVIDER = 'gemini'
    j.LLM_MODEL = os.environ['GEMINI_MODEL']
    j.LLM_API_KEY = os.environ['GEMINI_API_KEY']
    scenario = args.scenario
    label = scenario
    if os.getenv('QUALITY_ONLY') == '1':
        label += '-quality-only'
        def diagnostic_tick(self, triggers):
            from datetime import datetime, timezone
            return self._request('POST', '/v1/tick', 120, {'now': datetime.now(timezone.utc).isoformat(), 'available_triggers': triggers})
        j.BotClient.tick = diagnostic_tick
        print('DIAGNOSTIC ONLY: tick timeout raised to 120 seconds; not a timing-compliant score.', flush=True)
    judge = j.JudgeSimulator(j.create_provider())
    records = []
    original = j.LLMScorer.score
    def capture(self, action, *args, **kwargs):
        result = original(self, action, *args, **kwargs)
        records.append({'action': action, 'score': asdict(result), 'total': result.total})
        (ROOT / f'judge-{label}-results.json').write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
        return result
    j.LLMScorer.score = capture
    ok = judge.run(scenario)
    if records:
        mean = sum(r['total'] for r in records) / len(records)
        print(f'ACTUAL MEAN: {mean:.2f}/50 ({mean*2:.2f}%)')
        print(f'FALLBACK SCORES: {sum("Fallback" in r["score"]["specificity_reason"] for r in records)}')
    sys.exit(0 if ok else 1)
