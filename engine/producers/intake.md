# Producer runbook: intake
*Spec §5. Config: `engine/config/intake.yaml`. Level L2 (routes/files); people-map
updates stage at L1. Nightly 4:00. Never drops anything silently.*

## Before the run
Read `/context/theses.md` (classification targets), `/context/priorities.md`
(what makes something a DECIDE), and `/lessons/affinity.md` (dedup discipline).

## Gather
1. Every file in `/intake` (except README.md).
2. Emails inbound routed over (subject starts `intake:`) — inbound leaves these as
   `intake/` `.md` stubs with the link/text, so both paths converge here.

## Per item: fetch → classify → route → receipt
**Fetch/extract.** Files: read text / extract PDF. Links: fetch the page.
X/Twitter links: attempt fetch; if blocked or empty, **stop and write a RAN receipt
asking JC to paste the text** — never guess, never drop. Keep the stub in `/intake`.

**Classify** the content against `/context/theses.md` (Haiku-cheap first pass).
Pick the best-fit thesis, or "none".

**Route** (one primary route per item):

| If the item is… | Route | Action |
|---|---|---|
| a company / founder worth a look | **sourcing candidate** | write a KNOW tagged for sourcing to dedup vs Affinity; do not add to CRM here |
| evidence for a thesis | **thesis signal** | save the artifact to `state/research/<thesis>/`, bump the counter via `engine/signals.py` |
| a new/changed person | **people-map update** | stage an L1 diff to `context/people.md` inside the receipt — never apply live |
| relevant to `/context/priorities.md` | **DECIDE** | surface it with a recommendation |

**Receipt.** Write exactly one RAN queue item per drop via `qwrite` — one line on
what it was and where it went. Then remove the source file from `/intake` (the
receipt is now the audit trail). If it became a DECIDE/people-map item, that item
is separate from the receipt.

## Emit + commit
All writes go through `qwrite` (validated). `python3 engine/validate.py queue/*.md`
(0 errors), then commit `intake | processed N drops (…routes)`.

## Hard stops
No CRM writes (hand candidates to sourcing). No people.md live edits (stage L1).
Nothing sends. If unsure how to classify, route to DECIDE and ask — don't discard.
