# /os — Founding Spec
*Personal operating system for JC. Version 0.1 — July 2026.*
*This document is the constitution of the repo. Claude Code builds against it; the Friday retro amends it. If code and spec disagree, the spec wins until amended.*

---

## 1. Purpose

Automate execution so JC's time concentrates on judgment, approval, and upstream value creation. The unit of the system is the **decision request**, not the domain. Every automated process terminates in one of four states: DECIDE, APPROVE, KNOW, or RAN.

Success metric: JC clears the morning Daily in ≤10 minutes and nothing consequential happens without either his judgment or a logged autonomous action he can audit.

---

## 2. Directory layout (the state plane)

```
/os
  /context        ← identity, theses, priorities, people map, autonomy table, standing rules
  /queue          ← open decision requests, one .md file each, schema in §4
  /state          ← trackers as structured data (JSON/CSV): pipeline, LP universe,
                    net-worth model inputs, tasks, fantasy roster
  /lessons        ← corrections and rulings, one per file; the system's case law
  /engine         ← all producer code, the Daily renderer, configs, schedules
  /daily          ← rendered Daily artifacts, one per date (HTML + md)
  /archive        ← resolved queue items, moved on resolution; audit trail
```

Rules:
- Everything is a file. Notion / Affinity / Superhuman / Drive are **sources and sinks** the engine syncs with — never where truth lives.
- The repo is git-versioned. Producers commit their writes with structured messages (`producer: inbound | wrote 3 queue items`).
- `/context` files are short. Bloated instruction files degrade model output. One page per file, max.

---

## 3. The four planes

1. **State** — the directory above.
2. **Compute** — producers (§5). Loops with no voice: they write queue items and state; they never message JC directly.
3. **Review** — the Daily (§6). The only push surface.
4. **Action** — the autonomy ladder (§7).

---

## 4. Queue item schema

One markdown file per item: `/queue/YYYY-MM-DD-<producer>-<slug>.md`

```yaml
---
producer: inbound | sourcing | thesis | tasks | lp | finance | sports | political | education | fun
type: DECIDE | APPROVE | KNOW | RAN
title: one line
consequence_if_ignored: one line          # required; drives ranking
deadline: date or null
autonomy_level_of_action: L0-L3
status: open | resolved | expired
---

## What happened
## What I did about it
## Recommendation            # required for DECIDE; a producer that can't recommend isn't done thinking
## What would change my recommendation
## What I need from you
```

- DECIDE items: max 5 surfaced per Daily. Overflow is ranked by `consequence_if_ignored` and held.
- APPROVE items: must contain the exact staged action (full draft text, exact CRM field change) — approval means "execute verbatim."
- KNOW items: 3 sentences max each; link out for depth.
- RAN items: one line each; what executed, at what level, with what result.

---

## 5. Producer contracts

Each producer is a script (or Cowork scheduled task) with: a config file in `/engine/config/`, a cadence, an autonomy level, and a defined write surface. Producers are independent — one failing never blocks the Daily; the renderer notes "producer X did not report."

| Producer | Cadence | Level (start) | Writes | Notes |
|---|---|---|---|---|
| inbound | 6:00 / 12:00 / 17:00 | L1 | APPROVE (drafts, archive batches), DECIDE (judgment threads), KNOW | Superhuman MCP. Fetch by split, not bulk. Sending is permanently capped at L1. |
| sourcing | nightly scan; Mon rank | L1 | KNOW (signals), DECIDE (weekly top-5 with rec), APPROVE (Affinity adds) | StrictlyVC via sitemap scrape (not email bodies); YC batches; founder-departure signals. Dedup against Affinity before surfacing. |
| thesis | nightly | L0 | KNOW; DECIDE when a thesis crosses signal threshold ("time for a synthesis session") | Signal counts per active thesis tracked in /state. Synthesis itself is never scheduled — it's a triggered chat/Cowork session. |
| tasks | nightly sweep | L2 | /state/tasks.json; DECIDE (top-3 for the day) | Extracts commitments from email, calendar, and chat rulings. Requires substrate seeding in week 1. |
| lp | weekly enrichment; decay alerts | L0/L1 | DECIDE (who to touch + why), APPROVE (staged drafts) | Clay/PitchBook enrichment; Affinity last-touch decay (>60d on active targets). Outbound LP comms permanently capped at L1. |
| finance | monthly (25th) + threshold alerts | L0 permanent | DECIDE (max one action/month), KNOW (variance narrative) | Refreshes wealth-model inputs. Instrumentation only: no trades, no transfers, ever, at any level. |
| sports | in-season, event-driven | L0 | KNOW (fantasy card Sun AM, betting slate framed as thesis not picks, Detroit results) | Discussion stays in chat by design. |
| political | nightly | L0 | KNOW | Cross-spectrum sources forced in config; "what happened + why each side cares." MI/Detroit policy sub-signal. |
| education | weekly | L0 | KNOW (one concept, chosen by live deal flow) | Learning session itself happens in chat, on JC's initiation. |
| fun | Thursday | L0 | KNOW (one Detroit event, one date idea, one golf window vs weather) | Suggestions, never plans. |

**Meta-producer — the Friday retro (Cowork, Fridays 16:00, L1):**
Reviews the week: DECIDE overrides (recommendation-quality failures), unactioned KNOW items (cut sources), silent producers (kill or fix), chat corrections not yet in /lessons. Output: a staged change-list PR to /context and /engine configs. This producer is not optional; without it the system rots in ~6 weeks.

---

## 6. The Daily

- Rendered at 6:30 from open queue items. One HTML artifact in /daily plus a plain-md fallback.
- Section order fixed: **DECIDE → APPROVE → KNOW → RAN.**
- Delta pushes during the day only if an item's consequence crosses the urgency threshold defined in /context/thresholds.md. Silence otherwise.
- Resolving an item (JC replies/acts) moves it to /archive with the resolution noted — resolutions are training data for the retro.

---

## 7. Autonomy ladder

- **L0** observe & report → **L1** stage for approval → **L2** act & report in RAN → **L3** act silently.
- Levels live in `/context/autonomy.md`, per producer per action-type. Promotion requires 4 consecutive clean weeks in RAN and an explicit JC ruling logged to /lessons.
- **Permanent caps:** outbound sending of any communication (L1), anything touching money (L0), LP outreach (L1), CRM destructive edits (L1).

---

## 8. Surface routing

- **Claude Code (desktop app)** — owns /engine. Builds, tests, versions. Producers run headless via launchd/cron (4:00–6:15 batch window so the Daily is ready at 6:30).
- **Cowork** — owns judgment-bearing scheduled passes (inbound triage, Monday sourcing rank, Friday retro), pointed at /os as its working folder. Global instructions reference /context.
- **Chat** — owns thinking (deal debates, thesis synthesis, sports, education, ideas). Chat sessions end with rulings logged to /lessons or /state when a decision was made, so conversation output is never lost to the system.
- **The Daily** — the only push channel.

---

## 9. Build order

1. **Session 1 (Code):** repo skeleton, seed /context from CONTEXT_SEED.md, commit this spec, build the Daily renderer against fixture queue items, wire launchd.
2. **Session 2:** inbound producer (highest ROI; workflow already proven — port it, don't reinvent).
3. **Session 3:** sourcing producer (port the sitemap pipeline from the Brief engine) + tasks substrate.
4. **Week 2:** Friday retro goes live and governs everything after. Add remaining producers one per week, retro-gated.
5. The legacy Brush Park Brief keeps running until sourcing + political + sports producers cover it; then retire it. Nothing is retired before its replacement ships.

---

## 10. Amendment

Changes to this spec go through the Friday retro as staged diffs. Ad-hoc changes mid-week are allowed only with a /lessons entry explaining why the retro couldn't wait.
