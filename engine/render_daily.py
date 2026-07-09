#!/usr/bin/env python3
"""The Daily — markdown audit artifact (FOUNDING_SPEC §6).

The review plane is Claude rendering the queue as an interactive artifact (see
engine/producers/daily.md). This script produces only the git-versioned MARKDOWN
audit trail in /daily and refreshes stats.json. It NEVER sends, emails, or opens
anything — the system sends nothing, ever (standing-rule #0). Pure Python, no LLM.

Section order is fixed: DECIDE → APPROVE → KNOW → RAN. DECIDE ranked, capped at 5.
`consequence_if_ignored` is ranking metadata — shown only on DECIDE/APPROVE.

Editions:
  morning (default)  full → /daily/<date>.md            (7:00 Cowork task)
  evening (--since)  delta → /daily/<date>-pm.md         (17:00 Cowork task)
    items created/changed since the cutoff, plus urgency-threshold crossers.

Usage:
  python3 engine/render_daily.py [--date YYYY-MM-DD] [--queue DIR] [--out DIR]
  python3 engine/render_daily.py --since 07:00        # evening delta
"""
import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import PRODUCERS, load_open  # noqa: E402
import stats as stats_mod  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUEUE, DAILY = ROOT / "queue", ROOT / "daily"
DECIDE_CAP = 5
ORDER = ("DECIDE", "APPROVE", "KNOW", "RAN")
BLURB = {
    "DECIDE": "Your judgment required. Ranked; top 5 shown.",
    "APPROVE": "Staged and ready. Approval = execute verbatim (stage only, never send).",
    "KNOW": "No action needed. Awareness only.",
    "RAN": "Executed autonomously. Audit trail.",
}
_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.DOTALL)


def _by_type(items):
    buckets = {t: [] for t in ORDER}
    for it in items:
        buckets.get(it.type, buckets["KNOW"]).append(it)
    return buckets


def _held(decide):
    return decide[:DECIDE_CAP], max(0, len(decide) - DECIDE_CAP)


def _select(items, since_ts):
    if since_ts is None:
        return items
    return [it for it in items if it.changed_at >= since_ts or it.crosses_urgency()]


def _staged(it):
    m = _FENCE.search(it.body)
    return m.group(1).strip() if m else (
        it.section("What I did about it") or it.section("What happened"))


def render_md(day, buckets, edition="morning", since=None):
    head = f"# The Daily — {day}"
    if edition == "evening":
        head += f"  ·  evening edition (Δ since {since})"
    L = [head, "", "*Audit artifact. The live review surface is the `daily` "
         "artifact rendered in-session — this file is the git record.*", ""]
    total = sum(len(v) for v in buckets.values())
    if edition == "evening" and total == 0:
        L.append(f"_No changes since {since}. Nothing crossed the urgency threshold._\n")
    reported = sorted({it.producer for b in buckets.values() for it in b})
    silent = sorted(PRODUCERS - set(reported))
    for t in ORDER:
        items = buckets[t]
        shown, held = (_held(items) if t == "DECIDE" else (items, 0))
        L.append(f"## {t} ({len(items)})")
        L.append(f"_{BLURB[t]}_")
        if not shown:
            L.append("\n— nothing —\n")
        for it in shown:
            dl = f" · due {it.deadline}" if it.deadline else ""
            sev = f" · {it.severity}" if t in ("DECIDE", "APPROVE") else ""
            L.append(f"\n### [{it.id}] {it.title}\n`{it.producer}` · "
                     f"{it.meta.get('autonomy_level_of_action','')}{sev}{dl}")
            if t in ("DECIDE", "APPROVE"):   # consequence is ranking metadata
                L.append(f"> consequence if ignored: {it.meta.get('consequence_if_ignored','')}")
            if t == "DECIDE" and it.section("Recommendation"):
                L.append(f"\n**Recommendation:** {it.section('Recommendation')}")
            if t == "APPROVE":
                L.append(f"\n```\n{_staged(it)}\n```")
            if t in ("KNOW", "RAN"):
                gist = it.section("What happened") or it.section("What I did about it")
                if gist:
                    L.append(f"\n{gist}")
        if t == "DECIDE" and held:
            L.append(f"\n_+{held} more DECIDE held — resolve above to surface them._")
        L.append("")
    if silent:
        L.append(f"---\n_Producers silent: {', '.join(silent)}._")
    return "\n".join(L) + "\n"


def render(day, queue_dir, out_dir, since_ts=None, since_label=None):
    """Write the markdown audit artifact. since_ts set → evening delta (-pm)."""
    edition = "evening" if since_ts is not None else "morning"
    buckets = _by_type(_select(load_open(queue_dir), since_ts))
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-pm" if edition == "evening" else ""
    base = out_dir / f"{day}{suffix}"
    base.with_suffix(".md").write_text(
        render_md(day, buckets, edition, since_label), encoding="utf-8")
    return buckets, base


def _parse_since(s):
    if re.fullmatch(r"\d{1,2}:\d{2}", s):
        dt = datetime.combine(date.today(), datetime.strptime(s, "%H:%M").time())
    else:
        dt = datetime.fromisoformat(s)
    return dt.timestamp(), dt.strftime("%H:%M")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--out", type=Path, default=DAILY)
    ap.add_argument("--since", help="evening delta cutoff: 'HH:MM' or ISO datetime")
    a = ap.parse_args(argv[1:])
    datetime.strptime(a.date, "%Y-%m-%d")

    stats_mod.build()  # refresh stats.json for the artifact + KPI strip
    since_ts, since_label = (_parse_since(a.since) if a.since else (None, None))
    buckets, base = render(a.date, a.queue, a.out, since_ts, since_label)
    edition = "evening" if since_ts is not None else "morning"
    counts = " ".join(f"{t}:{len(buckets[t])}" for t in ORDER)
    print(f"rendered {base}.md  [{edition}]  ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
