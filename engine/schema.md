# Queue-item schema
*Canonical definition. FOUNDING_SPEC §4 is the constitution; this file is its
machine-checkable form. `engine/queue.py` enforces it; `engine/validate.py` lints
against it.*

One markdown file per open decision request:

```
/queue/YYYY-MM-DD-<producer>-<slug>.md
```

## Frontmatter (YAML)

| Field                     | Required | Values / rule                                              |
|---------------------------|----------|------------------------------------------------------------|
| `producer`                | yes      | inbound, sourcing, thesis, tasks, lp, finance, sports, political, education, fun |
| `type`                    | yes      | DECIDE, APPROVE, KNOW, RAN                                  |
| `title`                   | yes      | one line                                                   |
| `consequence_if_ignored`  | yes      | one line — drives DECIDE ranking                           |
| `deadline`                | yes      | `YYYY-MM-DD` or `null`                                     |
| `autonomy_level_of_action`| yes      | L0–L3                                                       |
| `status`                  | yes      | open, resolved, expired                                    |
| `severity`                | no       | high, medium, low (default medium) — ranking + delta-push  |

`severity` is a Session-1 extension of the spec schema so the renderer can rank
DECIDE deterministically (no LLM call at 6:30). See SPEC_QUESTIONS.md; the retro
may fold it into the spec.

## Body sections

```
## What happened
## What I did about it
## Recommendation            # REQUIRED for DECIDE — a producer that can't recommend isn't done thinking
## What would change my recommendation
## What I need from you
```

## Type-specific rules (enforced by the validator)

- **DECIDE** — non-empty `## Recommendation`. Max 5 surfaced per Daily; overflow
  ranked by `thresholds.md` and held.
- **APPROVE** — must contain the **exact staged action** (full draft text or exact
  CRM field change). Approval means "execute verbatim." The validator warns if the
  body has no fenced block or explicit staged content.
- **KNOW** — 3 sentences max each; link out for depth.
- **RAN** — one line: what executed, at what level, with what result.

## Lifecycle

`open` → resolved by JC → moved to `/archive` with the resolution noted
(resolutions are training data for the Friday retro). `expired` when a null-action
deadline passes unactioned.
