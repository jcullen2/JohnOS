"""Shared queue-item model: parse, validate, rank. Stdlib only (no deps → runs
under launchd on a bare Mac). Used by validate.py and render_daily.py.

Schema: engine/schema.md. Constitution: FOUNDING_SPEC.md §4.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

# Producers named for what they do. `thesis` is a counter-driven mechanism, not a
# scheduled fetch — it emits only the synthesis-session DECIDE (see SPEC_QUESTIONS).
PRODUCERS = {"inbound", "intake", "sourcing", "news", "policy", "thesis",
             "tasks", "network", "finance", "sports", "learn", "leisure", "retro"}
TYPES = {"DECIDE", "APPROVE", "KNOW", "RAN"}
STATUSES = {"open", "resolved", "expired"}
LEVELS = {"L0", "L1", "L2", "L3"}
SEVERITY = {"high": 3, "medium": 2, "low": 1}

# consequence_if_ignored is required only for DECIDE/APPROVE (it drives ranking /
# urgency); it is meaningless on KNOW/RAN and suppressed from their display.
REQUIRED = ("producer", "type", "title",
            "deadline", "autonomy_level_of_action", "status")
BODY_HEADS = ("What happened", "What I did about it", "Recommendation",
              "What would change my recommendation", "What I need from you")

_FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Item:
    path: Path
    meta: dict
    body: str
    sections: dict = field(default_factory=dict)

    @property
    def type(self) -> str: return str(self.meta.get("type", ""))

    @property
    def producer(self) -> str: return str(self.meta.get("producer", ""))

    @property
    def title(self) -> str: return str(self.meta.get("title", "")).strip()

    @property
    def deadline(self):
        d = self.meta.get("deadline")
        return None if d in (None, "null", "") else str(d)

    @property
    def severity(self) -> str:
        return str(self.meta.get("severity") or "medium").lower()

    @property
    def id(self) -> str:
        """Stable, human-readable id derived from the (stable) filename:
        <PRD>-<4hex>, e.g. INB-3a9f. Same file → same id across every render."""
        h = hashlib.md5(self.path.name.encode()).hexdigest()[:4]
        return f"{(self.producer[:3] or 'itm').upper()}-{h}"

    @property
    def changed_at(self) -> float:
        """Filesystem mtime — when the item was last created or edited."""
        try:
            return self.path.stat().st_mtime
        except OSError:
            return 0.0

    def crosses_urgency(self) -> bool:
        """thresholds.md: a mid-day delta-push item — DECIDE/APPROVE, high
        severity, deadline today or past."""
        from datetime import date
        return (self.type in ("DECIDE", "APPROVE") and self.severity == "high"
                and self.deadline is not None and self.deadline <= date.today().isoformat())

    def section(self, head: str) -> str:
        return self.sections.get(head, "").strip()

    def rank_key(self):
        """Lower sorts first: high severity, soonest deadline, stable by name."""
        return (-SEVERITY.get(self.severity, 2),
                self.deadline or "9999-99-99",
                self.path.name)


def _parse_frontmatter(text: str):
    """Minimal flat YAML: `key: value` per line. Values stay strings; `null`/
    empty → None; surrounding quotes stripped. Sufficient for our schema."""
    meta = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
            val = val[1:-1]
        meta[key.strip()] = None if val in ("", "null", "~") else val
    return meta


def _split_sections(body: str) -> dict:
    """Split markdown body on `## ` headings into {heading: content}."""
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = ""
        elif cur is not None:
            out[cur] += line + "\n"
    return out


def load(path: Path) -> Item:
    raw = Path(path).read_text(encoding="utf-8")
    m = _FM.match(raw)
    if not m:
        return Item(Path(path), {}, raw, {})
    meta = _parse_frontmatter(m.group(1))
    body = m.group(2)
    return Item(Path(path), meta, body, _split_sections(body))


def validate(item: Item):
    """Return (errors, warnings) as lists of strings. Errors fail the lint."""
    errs, warns = [], []
    m = item.meta

    for k in REQUIRED:
        if k not in m or (m[k] in (None, "") and k != "deadline"):
            errs.append(f"missing required field: {k}")

    if m.get("producer") not in PRODUCERS:
        errs.append(f"producer '{m.get('producer')}' not in {sorted(PRODUCERS)}")
    if m.get("type") not in TYPES:
        errs.append(f"type '{m.get('type')}' not in {sorted(TYPES)}")
    if m.get("status") not in STATUSES:
        errs.append(f"status '{m.get('status')}' not in {sorted(STATUSES)}")
    if m.get("autonomy_level_of_action") not in LEVELS:
        errs.append(f"autonomy_level_of_action '{m.get('autonomy_level_of_action')}'"
                    f" not in {sorted(LEVELS)}")
    if item.deadline and not _DATE.match(item.deadline):
        errs.append(f"deadline '{item.deadline}' is not YYYY-MM-DD or null")
    if "severity" in m and item.severity not in SEVERITY:
        errs.append(f"severity '{m.get('severity')}' not in {sorted(SEVERITY)}")
    if item.type in ("DECIDE", "APPROVE") and \
            not str(m.get("consequence_if_ignored") or "").strip():
        errs.append("consequence_if_ignored required for DECIDE/APPROVE (drives ranking)")

    if item.type == "DECIDE":
        if not item.section("Recommendation"):
            errs.append("DECIDE requires a non-empty '## Recommendation'")
        if item.severity == "medium" and "severity" not in m:
            warns.append("DECIDE has no explicit severity → ranked as medium")
    if item.type == "APPROVE":
        if "```" not in item.body and not item.section("What I did about it"):
            warns.append("APPROVE should contain the exact staged action verbatim")

    # naming: YYYY-MM-DD-<producer>-<slug>.md
    if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z]+-[a-z0-9-]+\.md$", item.path.name):
        warns.append("filename should be YYYY-MM-DD-<producer>-<slug>.md")

    return errs, warns


def load_open(queue_dir: Path):
    """All parseable items with status: open, sorted by rank_key."""
    items = [load(p) for p in sorted(Path(queue_dir).glob("*.md"))]
    return sorted([i for i in items if i.meta.get("status") == "open"],
                  key=Item.rank_key)
