# State
*Spec §2: trackers as structured data (JSON/CSV). The engine syncs these with
Notion / Affinity / Superhuman / Drive — but truth lives here, not there.*

Session 1 ships empty typed stubs so producers have a landing spot. **Week-1
migration** (seed list) fills them:

| File                     | Migrate from                          | Owner producer |
|--------------------------|---------------------------------------|----------------|
| `tasks.json`             | email + calendar + chat rulings sweep | tasks          |
| `theses.json`            | signal counts per active thesis       | thesis         |
| `motmot-tracker.json`    | Motmot investor tracker (P0–P2, ~15)  | inbound / lp   |
| `monaco-lp-universe.json`| 20 ranked LP targets                  | lp             |
| `wealth-model.json`      | Excel model **inputs** (not workbook) | finance        |
| `assembly-pipeline.json` | Affinity snapshot                     | sourcing       |

Rules:
- Structured only — no prose trackers. A producer reads/writes its own files.
- Commit writes with a structured message (`producer: tasks | +4 tasks`).
- Dedup before write (Affinity lesson). Never store secrets here.
