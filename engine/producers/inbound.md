# Producer runbook: inbound
*Spec §5. Config: `engine/config/inbound.yaml`. Run by Cowork/Claude (needs the
Superhuman MCP + judgment), not a bare Python cron. Level L1 — **nothing ever
sends.** This file is the contract; port it, don't improvise.*

## Before the run
Read `/context/{identity,people,priorities,standing-rules}.md` and
`/lessons/superhuman.md`. Load resolved thread ids from `/archive` so you don't
re-surface a thread JC already handled.

## Fetch (by split, never bulk — /lessons/superhuman.md)
For each split in `config.splits`, in order:
`list_threads(split=<name>, limit=threads_per_split)`. Triage from the snippet +
participants + labels. This is cheap and enough for most items. Only call
`get_thread` when you must read the full thread to draft a reply or make a
judgment call — cap at `full_reads_per_run`. **Never** `get_thread` newsletters or
bulk-read Other. Never use `query_email_and_calendar` (it truncates).

## Triage → one queue item per actionable thread
Classify each thread (Haiku-cheap first pass, escalate only the ambiguous):

| Signal | Type | What the item carries |
|---|---|---|
| Real person, needs JC's decision (terms, intro yes/no, conflict) | **DECIDE** | recommendation + what you need |
| Real person, routine reply JC would send | **APPROVE** | the exact draft, verbatim |
| Batch of low-value Other (newsletters, notifications) to clear | **APPROVE** | the archive batch: exact thread ids + one-line reason |
| Worth knowing, no action (deal news, FYI, portfolio update) | **KNOW** | ≤3 sentences + link |
| Already handled, spam, or noise | *skip* | — |

Set `severity` (high only for same-day / deal-critical / relationship-risk),
`deadline` where the thread implies one, `consequence_if_ignored` always.
Skip Pitch/Other threads that are pure noise — a quiet queue beats a padded one.

## Emit + commit
Write every item through the validated writer — never hand-format frontmatter:

```python
from qwrite import write_item   # engine/ on sys.path
write_item("queue", producer="inbound", type="DECIDE", slug="<thread-slug>",
           title="...", consequence_if_ignored="...", severity="high",
           deadline="YYYY-MM-DD", autonomy_level_of_action="L1",
           what_happened="...", what_i_did="staged draft below; not sent",
           recommendation="...", what_would_change="...", what_i_need="...")
```

APPROVE items put the exact staged action in `what_i_did` inside a ```fenced```
block — the renderer surfaces that verbatim as "approval = execute this."

Then: `python3 engine/validate.py queue/*.md` (must be 0 errors) and commit
`inbound | wrote N queue items (D DECIDE, A APPROVE, K KNOW)`. The 6:30 renderer
does the rest. If a split fails, write what you have and note the gap — one split
failing never blocks the Daily.

## Calendar rule (standing-rule #4)
No staged draft may propose a specific time or date without first checking Google
Calendar via MCP (`list_events` over the window). Note it verbatim in the item:
*"calendar checked, free"* or *"calendar checked, conflict → proposed X."* No
calendar access → propose no specific time; ask JC.

## Hard stops
The system sends nothing, ever (standing-rule #0). Archiving, labeling, trashing,
marking spam, unsubscribing — none, ever. Drafts stage only. Network/LP threads:
stage, never automate (standing-rule #2).
