"""Validated queue-item writer. Every producer emits items through this so the
queue can never drift from the schema (engine/schema.md). Builds the markdown,
validates it via qitem, and writes the canonical filename. Stdlib only.

    from qwrite import write_item
    write_item(QUEUE, producer="inbound", type="DECIDE", slug="motmot-cap",
               title="...", consequence_if_ignored="...", severity="high",
               autonomy_level_of_action="L1", deadline="2026-07-10",
               recommendation="...", what_i_need="...")
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from qitem import BODY_HEADS, load, validate

_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(s: str) -> str:
    return _SLUG.sub("-", s.lower()).strip("-")[:48] or "item"


def build(*, producer, type, title, consequence_if_ignored,
          autonomy_level_of_action, status="open", deadline=None, severity=None,
          extra=None, what_happened="", what_i_did="", recommendation="",
          what_would_change="", what_i_need="") -> str:
    """Return the full markdown text for a queue item (frontmatter + body).
    `extra` is an optional dict of extra frontmatter (e.g. sourcing thesis/round)."""
    fm = [f"producer: {producer}", f"type: {type}",
          f"title: {title}",
          f"consequence_if_ignored: {consequence_if_ignored}",
          f"deadline: {deadline or 'null'}",
          f"autonomy_level_of_action: {autonomy_level_of_action}",
          f"status: {status}"]
    if severity:
        fm.append(f"severity: {severity}")
    for k, v in (extra or {}).items():
        fm.append(f"{k}: {v}")
    bodies = dict(zip(BODY_HEADS,
                      [what_happened, what_i_did, recommendation,
                       what_would_change, what_i_need]))
    body = "\n".join(f"## {h}\n{bodies[h].strip()}\n" for h in BODY_HEADS)
    return "---\n" + "\n".join(fm) + "\n---\n\n" + body


def write_item(queue_dir, *, slug=None, on=None, **fields) -> Path:
    """Build, validate, and write a queue item. Raises ValueError on a schema
    violation — an invalid item never reaches the queue. Returns the path."""
    text = build(**fields)
    day = on or date.today().isoformat()
    slug = slugify(slug or fields["title"])
    path = Path(queue_dir) / f"{day}-{fields['producer']}-{slug}.md"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    errs, _ = validate(load(path))
    if errs:
        path.unlink()
        raise ValueError(f"refusing to write invalid item:\n  " + "\n  ".join(errs))
    return path
