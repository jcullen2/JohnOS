# Producer runbook: sourcing
*Spec §5. Config: `engine/config/sourcing.yaml`. Level L1. Nightly scan + Monday
6:45 ranked DECIDE. Ports the legacy-digest pattern (`/lessons/digest-pattern.md`).*

## Before the run
Read `/context/theses.md` (only surface thesis-aligned candidates),
`/lessons/strictlyvc.md` (sitemap, not email bodies), `/lessons/affinity.md`
(dedup before surfacing).

## Nightly (KNOW signals)
1. **Fetch** each source in config: StrictlyVC via sitemap → beehiiv pages,
   walking h2/h3/p against the funding-section headings; YC batch filtered to
   industrial/hard-tech; founder-departure signals; intake-routed candidates.
2. **Haiku triage** — keep only thesis-aligned companies/founders; drop the rest.
3. **Dedup against Affinity** (`search_companies_top_matches`). Anything already in
   the CRM is not net-new — annotate, don't surface as new.
4. **Write** up to `caps.nightly_signals` KNOW items (rank the rest, hold, note count).
   Each: what it is, thesis fit, why now, Affinity status. Bump the thesis counter
   via `engine/signals.py` for each real signal.

## Monday 6:45 (ranked DECIDE)
Rank the week's net-new candidates; write the top-5 as DECIDE, each with a
recommendation and an explicit what-would-change-it. Affinity adds stage as APPROVE
(exact list + fields), never written live.

## Emit + commit
All writes via `qwrite`; `validate.py` clean; commit
`sourcing | N signals` / `sourcing | Monday top-5 DECIDE`.

## Hard stops
No live CRM writes (adds stage L1 APPROVE). No outreach. Dedup is non-negotiable.
