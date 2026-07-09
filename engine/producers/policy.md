# Producer runbook: policy
*Spec §5. Config: `engine/config/policy.yaml`. Level L0. Nightly 4:45. KNOW only,
capped per ring. Cross-spectrum sources are forced in config.*

## Before the run
Load the three rings and their caps. Ring 3's `forced_sources` (left/center/right)
are mandatory — pull from all three columns, never one side.

## Run — three rings
1. **Civic** (Detroit/MI): city government, Lansing, economic development, major
   local institutions/projects. Up to `cap` KNOW items.
2. **Thesis policy** (national, touching active theses): defense appropriations,
   reshoring/tariffs/industrial policy, energy, immigration incl. EB-3. Up to `cap`.
   Bump the matching thesis counter (`engine/signals.py`) when an item is real evidence.
3. **National politics** (cross-spectrum): up to `cap`. **Every item must carry both
   "why the left cares" and "why the right cares"** — framing is "what happened +
   why each side cares." Report positions, attribute them, never editorialize.

Haiku triage each ring; keep only what's new and material; hold overflow, note count.

## Emit + commit
All writes via `qwrite`; `validate.py` clean; commit `policy | N KNOW (3 rings)`.

## Hard stops
KNOW only. Ring 3 without both sides is a defect — hold the item rather than ship
one-sided. No editorializing.
