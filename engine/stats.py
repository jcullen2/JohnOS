#!/usr/bin/env python3
"""Build state/stats.json — the numbers behind the Daily KPI strip. Derived from
/queue (open state), /state (thesis counters), and /archive (throughput/funnel).
Stdlib only; no network, no LLM.

    python3 engine/stats.py            # write state/stats.json, print a summary
    from stats import build            # returns the dict and writes the file
"""
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import PRODUCERS, load, load_open  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUEUE, ARCHIVE, STATE = ROOT / "queue", ROOT / "archive", ROOT / "state"
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_RESOLVED = re.compile(r"^## Resolution \((\d{4}-\d{2}-\d{2})", re.M)


def _age_days(item, today):
    m = _DATE.match(item.path.name)
    if not m:
        return 0
    return (today - date.fromisoformat(m.group(1))).days


def _week_counts(paths, today, producer):
    """(this-week, last-week) counts of a producer's items by filename date."""
    this = last = 0
    for p in paths:
        m = _DATE.match(p.name)
        if not m or producer not in p.name:
            continue
        age = (today - date.fromisoformat(m.group(1))).days
        if 0 <= age < 7:
            this += 1
        elif 7 <= age < 14:
            last += 1
    return this, last


def build():
    today = date.today()
    items = load_open(QUEUE)
    decide = [i for i in items if i.type == "DECIDE"]
    approve = [i for i in items if i.type == "APPROVE"]
    reporting = sorted({i.producer for i in items})

    # throughput: resolutions recorded in /archive over the last 7 days
    arch = list(ARCHIVE.glob("*.md"))
    resolved_7d = 0
    for p in arch:
        m = _RESOLVED.search(p.read_text(encoding="utf-8"))
        if m and (today - date.fromisoformat(m.group(1))).days < 7:
            resolved_7d += 1

    # sourcing funnel: signals surfaced this week vs last (queue + archive)
    allpaths = list(QUEUE.glob("*.md")) + arch
    src_this, src_last = _week_counts(allpaths, today, "-sourcing-")

    theses = {}
    tf = STATE / "theses.json"
    if tf.exists():
        theses = json.loads(tf.read_text())["theses"]

    stats = {
        "generated": today.isoformat(),
        "queue": {
            "decide_open": len(decide),
            "decide_oldest_age_days": max((_age_days(i, today) for i in decide), default=0),
            "approve_staged": len(approve),
            "due_today": sum(1 for i in items if i.deadline == today.isoformat()),
            "total_open": len(items),
            "by_producer": {p: sum(1 for i in items if i.producer == p) for p in reporting},
        },
        "producers": {
            "reporting": reporting,
            "silent": sorted(PRODUCERS - set(reporting)),
            "n": len(reporting), "m": len(PRODUCERS),
        },
        "throughput": {"resolved_last_7d": resolved_7d, "archive_total": len(arch)},
        "sourcing_funnel": {"this_week": src_this, "last_week": src_last},
        "thesis_counters": {
            k: {"signals": v.get("signals", 0), "threshold": v.get("threshold"),
                "crossed": v.get("signals", 0) >= v.get("threshold", 1e9)}
            for k, v in theses.items()
        },
    }
    (STATE / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


if __name__ == "__main__":
    s = build()
    q = s["queue"]
    print(f"stats.json: {q['total_open']} open · DECIDE {q['decide_open']} "
          f"(oldest {q['decide_oldest_age_days']}d) · APPROVE {q['approve_staged']} · "
          f"due today {q['due_today']} · producers {s['producers']['n']}/{s['producers']['m']} · "
          f"resolved 7d {s['throughput']['resolved_last_7d']}")
