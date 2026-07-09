# The OS — repo guide for Claude
*Personal operating system for JC. The constitution is `FOUNDING_SPEC.md`; it
wins over code until amended by the Friday retro.*

## Before any substantial work
1. Read `/context` (identity, priorities, people, theses, autonomy, standing-rules,
   thresholds, **voice**, **feedback-loops**) and `/lessons` (hard-won tool
   knowledge — do not relearn it).
2. Read the relevant section of `FOUNDING_SPEC.md`. Build against it; don't redesign it.

## Standing rules (full text in `/context/standing-rules.md` — non-negotiable)
1. **Never send, archive, or act on email without explicit clearance.** Drafts stage only.
2. **Never automate outbound LP communications.**
3. **Voice in drafts is JC's own** — concise, warm-direct, zero AI filler.
4. **Distinguish sourced fact from inference.** Flag gaps; don't silently estimate.
5. **Pause only for** destructive/irreversible actions, scope changes, or inputs only
   JC can provide. Otherwise proceed and report.
6. **Comprehensive tiered briefings > streams of pings.** The Daily is the only push channel.

## Permanent autonomy caps (`/context/autonomy.md`)
Sending any comms → L1 · Anything touching money → L0 · LP outreach → L1 · CRM
destructive edits → L1. These never promote.

## The shape of the system (spec §2–§3)
Everything is a file. Notion / Affinity / Superhuman / Drive are sources & sinks, never
truth. Four planes: **State** (`/context`,`/queue`,`/state`,`/lessons`,`/archive`) ·
**Compute** (producers in `/engine` — loops with no voice) · **Review** (the Daily) ·
**Action** (the autonomy ladder). Every process terminates in DECIDE / APPROVE / KNOW / RAN.

## Engine
- `engine/qitem.py` — queue-item model (parse/validate/rank), stdlib only.
- `engine/validate.py` — lint queue files: `python3 engine/validate.py`.
- `engine/render_daily.py` — build the Daily: `python3 engine/render_daily.py`. Pure
  Python, no LLM call — the 6:30 job is deterministic and free.
- `engine/schema.md` — the queue-item schema. `engine/schedule/` — launchd jobs.

## Rules of the road
- `/context` files stay ≤1 page. Bloated instruction files degrade output (`/lessons`).
- Producers commit their writes: `producer: <name> | wrote N queue items`.
- Resolved queue items move to `/archive` with the resolution noted (retro training data).
- Spec ambiguity → log it in `SPEC_QUESTIONS.md`, don't guess. Mid-week spec changes need
  a `/lessons` entry saying why the retro couldn't wait.
- **Don't build producers ad hoc.** Build order and producer contracts are spec §5/§9;
  new producers are retro-gated after week 2.
