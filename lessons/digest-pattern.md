# Lesson: The digest pattern

The legacy digest is the **proven pattern to port** for every monitoring producer
(sourcing, news, policy) — do not rebuild from scratch.

- **Config-driven fetch** — sources live in a `.yaml`, ~40 of them, never hardcoded.
- **Cheap-model triage** — a Haiku pass does the first filter; expensive reasoning
  runs only on what survives.
- **Hard per-section caps** — every section has a fixed max; overflow is ranked and held.
- **HTML render** at the end.

Reuse the sitemap technique (`/lessons/strictlyvc.md`) and Affinity-dedup
(`/lessons/affinity.md`). Retire the legacy digest only after sourcing + news +
policy fully cover it (spec §9) — nothing is retired before its replacement ships.
