# Schedules (launchd)
*Spec §8: producers run headless in the pre-dawn batch window so the Daily is
ready at 7:00. Claude Code / launchd owns `/engine`; Cowork owns judgment-bearing
passes (inbound triage, Monday sourcing rank, Friday retro).*

## Install
```bash
bash engine/schedule/install.sh      # rewrites paths, loads every *.plist
launchctl list | grep com.jc.os      # verify
```
`install.sh` substitutes `__OS_ROOT__` with this repo's absolute path into
`~/Library/LaunchAgents/` and loads each job. Re-run after editing any plist.
**Nothing is enabled until JC confirms at GATE 3** — until then, run producers by
hand and inspect the queue.

## The Daily — two Cowork tasks (not launchd)
The review plane is **Claude rendering the queue as an interactive artifact**
(`engine/producers/daily.md`). It is **not** a launchd job and **sends nothing**
(standing-rule #0) — there is no email, no browser-open, no push.

| Cowork task | Time | Runs | Surface |
|---|---|---|---|
| Daily (full) | **7:00** | `daily.md` runbook → `render_daily.py` | interactive artifact + `/daily/<date>.md` audit |
| Daily (delta) | **17:00** | `daily.md` → `render_daily.py --since 07:00` | delta artifact + `/daily/<date>-pm.md` audit |

The evening edition shows only items created/changed since 07:00 plus anything that
crossed the urgency threshold (`/context/thresholds.md`). Use **Cowork's native task
notifications** — nothing custom. `render_daily.py` writes the git-versioned
markdown audit and refreshes `state/stats.json`; the artifact is the live surface.

## Producer batch window (4:00–6:45)
Producers write queue items **before 6:45** so the 7:00 Daily sees them. One plist
per producer; staggered so they don't contend. A producer that fails writes what
it has and the renderer just notes it silent — one failure never blocks the Daily.

| Producer | Schedule | Level | Notes |
|---|---|---|---|
| intake | nightly 4:00 | L2 | drains `/os/intake` + `intake:` emails; routes + RAN receipts |
| sourcing | nightly 4:15; Mon 6:45 rank | L1 | StrictlyVC sitemap, YC, founder-departures; Mon adds top-5 DECIDE |
| news | nightly 4:30 | L0 | portfolio/competitors/market/Detroit; KNOW, capped |
| policy | nightly 4:45 | L0 | three rings; KNOW, capped per ring |
| tasks | nightly 5:00 | L2 | email+calendar sweep → tasks.json; top-3 DECIDE |
| network | Mon 5:15 | L0/L1 | Affinity decay >60d; DECIDE + staged drafts (never auto-sends) |
| finance | 25th 5:30 + alerts | L0 🔒 | model-input refresh; ≤1 DECIDE/mo; nothing executes |
| learn | Wed 5:45 | L0 | one concept from live deal flow; KNOW |
| leisure | Thu 5:45 | L0 | Detroit event / date idea / golf window; KNOW |
| sports | in-season, event-driven | L0 | fantasy Sun AM, slates as analysis, Detroit results; KNOW |
| thesis | 6:15 (after fetchers) | L0 | rolls up signal counters; synthesis DECIDE on threshold |

## Adding a producer job
1. Copy a producer plist, set `Label` `com.jc.os.<producer>`.
2. Point `ProgramArguments` at its entrypoint (runbook via Cowork, or a script).
3. Set `StartCalendarInterval` inside **4:00–6:45**.
4. `bash engine/schedule/install.sh`.

The **Friday retro** (Cowork, 17:00, L1) is not a launchd job — it runs in Cowork
pointed at `/os`. See spec §5 and `engine/producers/retro.md`.
