# Spec questions & inferences
*Flagged rather than guessed. Resolve in the first Friday retro or inline; each is
low-stakes and reversible.*

## 6. `thesis` kept as a producer id (Phase 0 list omitted it)
The naming sweep's producer list was inbound, intake, sourcing, news, policy,
tasks, network, finance, sports, learn, leisure, retro — no `thesis`. But spec §5
still defines the thesis synthesis-session DECIDE, and it needs an attribution
home. **Decision:** kept `thesis` as a valid producer id used only for that
counter-driven DECIDE (no scheduled fetch of its own). Not an autonomy question.
**Confirm:** keep `thesis` as the emitter, or attribute the DECIDE to whichever
fetcher trips the counter?

## 7. Daily email = the one sending carve-out
Phase 1 grants the `daily` renderer an L2 exception to email JC's own address.
Encoded in `/context/autonomy.md` as a `daily` row + an explicit note on the
permanent send cap. No other producer may send. Flagging because it is the single
exception to standing-rule #1.

## 1. DECIDE ranking needs a signal the schema didn't carry — added `severity`
Spec §4 says DECIDE overflow is "ranked by `consequence_if_ignored`," but that field
is free text — not rankable deterministically without an LLM call at render time,
which would make the 6:30 job slow, nondeterministic, and token-costly.
**Inference:** added an optional `severity: high|medium|low` field (default medium)
that producers set. The renderer ranks by severity → deadline → filename
(`/context/thresholds.md`). Rendering stays pure Python.
**Decision needed:** keep `severity`, or fold ranking into the retro another way?

## 2. `/context/thresholds.md` didn't exist in the seed — created it
Spec §6 references `/context/thresholds.md` for the mid-day delta-push urgency
threshold; the CONTEXT_SEED had no such file. **Inference:** created it with a
conservative rule — a delta pushes only if DECIDE/APPROVE **and** severity high
**and** deadline today-or-past. Everything else waits for the Daily.
**Decision needed:** confirm the push threshold; tighten or loosen.

## 3. "Producer did not report" needs a roster
Spec §5 says the renderer notes when a producer is silent. With no producers live,
the renderer derives "silent" as the full producer enum minus producers that wrote
today. Once producers have schedules, silence should mean "scheduled but didn't
write," not "doesn't exist yet." **Revisit when producers land (Session 2+).**

## 4. State trackers are stubbed, not migrated
Kickoff §boundaries: don't touch external systems this session. `/state` has a README
and empty typed seed files (`tasks.json`, `theses.json`, trackers). Real migration
(Motmot tracker, Monaco LP universe, wealth-model inputs, Affinity snapshot) is week-1
work per the seed. **No action needed — noted for continuity.**

## 5. Redline the `/context` files
Per the seed header, anything wrong in `/context` propagates everywhere. The files are
a faithful split of CONTEXT_SEED.md; `autonomy.md` and `thresholds.md` contain the only
Session-1 additions (the table structure and the numbers). **Please redline before the
first producer reads them.**
