# Thresholds
*Referenced by FOUNDING_SPEC §6. Governs when a delta may push mid-day and how
the Daily ranks. INFERRED for Session 1 — redline these numbers; see
SPEC_QUESTIONS.md.*

## Mid-day delta push (the only interruption of Daily silence)

A queue item may trigger a push **before** the next Daily only if **all** hold:

- `type: DECIDE` or `APPROVE`, **and**
- `severity: high`, **and**
- `deadline` is today or already passed.

Everything else waits for the 6:30 Daily. Silence is the default.

## DECIDE ranking (Daily + overflow)

DECIDE items are ranked, top 5 surfaced, remainder held:

1. `severity` desc — `high` (3) > `medium` (2) > `low` (1); unset = medium.
2. `deadline` asc — soonest first; null deadlines last.
3. Filename asc — stable tiebreak.

`severity` is an optional queue field producers set alongside
`consequence_if_ignored` (a producer that can't recommend can't rank its own
output either). Absent it, items rank as medium.

## Source hygiene (retro input)

- A KNOW source with **0 opened items in 2 weeks** is a cut candidate.
- A producer **silent 3 consecutive runs** is a kill-or-fix candidate.
