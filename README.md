# JohnOS

Personal operating system for JC. Automates execution so JC's time concentrates on
judgment, approval, and upstream value creation. Every automated process terminates
in one of four states: **DECIDE · APPROVE · KNOW · RAN**, surfaced once a day in the
Daily.

- **`FOUNDING_SPEC.md`** — the constitution. Read it first.
- **`CLAUDE.md`** — orientation for any Claude session working here.
- **`/context`** — identity, priorities, people, theses, autonomy, standing rules.
- **`/lessons`** — hard-won tool knowledge; do not relearn it.
- **`/queue`** — open decision requests (schema: `engine/schema.md`).
- **`/engine`** — the Daily renderer, the queue model, validator, schedules.
- **`/state` `/daily` `/archive`** — trackers, rendered Dailies, resolved-item audit trail.

## Quick start
```bash
python3 engine/validate.py                        # lint the queue
python3 engine/render_daily.py                    # build today's Daily → /daily
python3 engine/render_daily.py --date 2026-07-09  # a specific date
open daily/2026-07-09.html
bash engine/schedule/install.sh                   # wire the 6:30 launchd job (macOS)
```
No dependencies — stdlib Python 3 only. The renderer makes no network or LLM call.
