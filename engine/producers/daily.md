# Producer runbook: daily (the review plane)
*Spec §6. The review surface is **Claude rendering the queue as an interactive
artifact** — there is no email, no push, no send (standing-rule #0). Triggered by
"daily" in any session with `~/os` access, and by the 7:00 / 17:00 Cowork tasks.*

## On "daily"
1. Refresh `state/calendar-week.json` from Google Calendar MCP (`list_events` for
   the current Mon–Sun) so the week view is live.
2. `python3 engine/render_daily.py` (morning) or `--since 07:00` (evening delta).
   Refreshes `state/stats.json` and writes the git-versioned md audit.
3. `python3 engine/render_artifact.py > daily/<date>-review.html`, then publish it
   with the Artifact tool. ONE artifact — overflow collapses behind expanders,
   never a separate page.

## Artifact layout
- **KPI strip** (from stats.json): DECIDE open + oldest-age days · APPROVE staged ·
  due today · sourcing this week vs last · producers reporting **N/M** (name the
  silent ones). Red the strip when DECIDE oldest-age > 2d or read-time trend breaches.
- **DECIDE** rows (ranked, ≤5; overflow expander): title, ID, severity, deadline,
  consequence, recommendation. Buttons: **Do-it · Discuss · Skip**.
- **APPROVE** rows: title, ID, expandable **exact staged draft**. Buttons:
  **Approve · Edit · Skip**. Show the "calendar checked" note when present.
- **KNOW**: grouped by producer, each group a collapsed **expander** (sourcing digest,
  news 4, policy 4, …). Suppress consequence lines here.
- **RAN**: one-liners, newest first.
- **Close out the day** button at the foot.

## Executing rulings (in-session, within autonomy caps)
Every button yields a ruling token `<VERB> <ID>` (e.g. `APPROVE INB-0251`). Collect
JC's taps and execute:

| Ruling | Action |
|---|---|
| **Approve** (APPROVE) | Stage the draft via Superhuman `create_or_update_draft`. **Never send** (standing-rule #0). Resolve the item. |
| **Do-it** (DECIDE) | Execute the recommendation **within the producer's autonomy cap** (`/context/autonomy.md`). Money/L0, LP outreach, CRM-destructive → stage only, never execute. Resolve with the action noted. |
| **Edit** | Apply JC's edit to the staged draft, re-stage. **Append the before→after to `state/voice-corrections.jsonl`** (voice loop) so voice.md learns. Leave open for re-approval. |
| **More / Pass / Get-me-in / Watch** (SOURCING) | Update `state/sourcing-prefs.json`: More → raise that thesis weight + record the liked signature; Pass → lower it + record to suppress near-dupes; Get-me-in → stage a warm-intro DECIDE + record in `met`; Watch → add to `watching`. This is the sourcing taste loop — it changes the next scan. |
| **Discuss** | Leave open; capture the thread for a chat/Cowork session. |
| **Skip** | Leave open (or mark per JC); no action. |
| **Close out the day** | `python3 engine/resolve.py <item> "<ruling note>" --ruling <VERB>` for each ruled item → `/archive` + `state/rulings.jsonl` (retro training data), then commit `daily | closed out N items (…)`. |

Applying rulings **is** the living system (`/context/feedback-loops.md`) — every
tap changes tomorrow's Daily. Never skip the prefs/voice writes on close-out.

## Hard stops
The system sends nothing, ever. Approvals stage drafts only. No money executes at
any level. No destructive CRM edits. If a Do-it would exceed a cap, stage and ask.
