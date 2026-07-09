# Session 1 kickoff — paste this into Claude Code

Setup first (you, 2 minutes): make a folder `~/os`, drop `FOUNDING_SPEC.md` and `CONTEXT_SEED.md` into it, open Claude Code (desktop app → Code tab) pointed at `~/os`. Then paste:

---

Read FOUNDING_SPEC.md and CONTEXT_SEED.md in this folder before doing anything. The spec is the constitution — build against it, don't redesign it.

Session 1 scope, in order:

1. Initialize git. Create the directory skeleton from spec §2.
2. Split CONTEXT_SEED.md into the /context and /lessons files it specifies. Show me the /context files for redline before committing — anything wrong there propagates.
3. Write /engine/schema.md capturing the queue-item schema (spec §4) and a validator script that lints queue files against it.
4. Build the Daily renderer: reads open /queue items, renders DECIDE → APPROVE → KNOW → RAN as a clean HTML file in /daily (plus a markdown fallback), ranks DECIDE by consequence_if_ignored, caps DECIDE at 5. Create 6–8 realistic fixture queue items across all four types and render a sample Daily so I can judge the format before any real producer exists.
5. Write a CLAUDE.md at repo root (≤1 page): points to the spec, states the standing rules from /context/standing-rules.md, and instructs future sessions to read /context and /lessons before substantial work.
6. Wire a launchd job that runs the renderer at 6:30am daily. Document how to add producer jobs to the 4:00–6:15 batch window.
7. Commit everything with clear messages. End by telling me exactly what Session 2 (inbound producer) needs from me — connector access, config decisions, nothing else.

Boundaries: don't build any producer yet. Don't touch email, Affinity, or any external system this session. If the spec is ambiguous, flag it in a SPEC_QUESTIONS.md instead of guessing.

---

# After Session 1

- Session 2 prompt lives here too: "Read the spec, /context, and /lessons. Build the inbound producer per spec §5 — port the proven Superhuman workflow from /lessons (split-based fetching), write APPROVE/DECIDE/KNOW queue items per schema, level L1, nothing sends ever. Test against my real inbox read-only, show me the queue items it would write before enabling the schedule."
- Set up the Cowork side once the repo exists: point Cowork's working folder at ~/os, paste the global-instructions block (identity + standing rules from /context), and schedule the Friday retro per spec §5.
