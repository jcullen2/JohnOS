# Producer runbook: news
*Spec §5. Config: `engine/config/news.yaml`. Level L0. Nightly 4:30. KNOW only,
hard-capped. Digest pattern (`/lessons/digest-pattern.md`).*

## Before the run
Load the section watchlists/topics from config. Portfolio + competitor names also
live in `/state` — prefer those over the config seed as they fill in.

## Run
For each section (portfolio, competitors, market_color, detroit_business,
detroit_sports):
1. **Fetch** headlines for the watchlist/topics.
2. **Haiku triage** — keep only what's genuinely new and material; drop noise and
   anything already surfaced this week.
3. **Write** up to the section `cap` as KNOW items, ≤3 sentences each, link out.
   Hold overflow, note the count.

Market_color items that are real thesis evidence bump the matching thesis counter
(`engine/signals.py`). Detroit sports = results/scores only (analysis is the sports
producer's job).

## Emit + commit
All writes via `qwrite`; `validate.py` clean; commit `news | N KNOW (by section)`.

## Hard stops
KNOW only — never a DECIDE or a draft. Respect caps; a padded digest is a failure.
