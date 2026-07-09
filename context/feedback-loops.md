# What makes this living, not static
*A static system renders state. A living system lets each interaction change the
next render. Every review action here becomes an input to a producer or the retro.
These are the closed loops and where each is wired.*

## The five loops

1. **Voice** — inbound drafts against `/context/voice.md`. When you tap **Edit** on
   a draft, the before→after is appended to `/state/voice-corrections.jsonl`; the
   Friday retro folds recurring corrections back into `voice.md`. Your drafts sound
   more like you every week. *(Wired: voice.md · daily close-out logs EDIT.)*

2. **Sourcing taste** — every candidate carries **More like this / Get me in /
   Watch / Pass**. Those rulings update `/state/sourcing-prefs.json` (thesis
   weights + liked/passed signatures). The sourcing producer **reads prefs on its
   next scan** to rank and filter — so it chases what you react to and stops
   surfacing what you pass on. *(Wired: sourcing.yaml `preferences` · daily applies
   MORE/PASS/MEET/WATCH.)*

3. **Rulings** — every DECIDE/APPROVE ruling is appended to `/state/rulings.jsonl`
   and the resolved item lands in `/archive` with your ruling noted. The retro
   mines these for override patterns (where your call ≠ the recommendation) and
   stages fixes to the producer that got it wrong. *(Wired: `resolve.py --ruling`.)*

4. **Theses** — sourcing/news/policy/intake bump `/state/theses.json` counters via
   `signals.py`; at threshold the thesis mechanism fires a synthesis DECIDE. Your
   attention compounds into "time to go deep on X." *(Wired: signals.py.)*

5. **Read-time & silence** — `stats.json` tracks queue age, throughput, and
   producers reporting N/M. Two Dailies over ≤10 min, or a producer silent three
   runs, is automatic retro agenda — the system flags its own decay. *(Wired:
   stats.py · retro.md, Phase 3.)*

## The integrator
Inline loops (2, 4) change behavior **immediately** — next scan. The **Friday
retro** is the weekly integrator for the slower loops (1, 3, 5): it reads the logs
and stages a change-list to `/context` and configs for your approval. Nothing
mutates `/context` silently; the loop always closes through a diff you see.

## The test
Ask of any feature: *does tomorrow's Daily differ because of what I did in today's?*
If no, it's a static report. If yes, it's part of the organism.
