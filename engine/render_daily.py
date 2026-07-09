#!/usr/bin/env python3
"""The Daily renderer (FOUNDING_SPEC §6).

Reads open /queue items and renders one self-contained HTML artifact plus a
markdown fallback into /daily. Section order is fixed: DECIDE → APPROVE → KNOW →
RAN. DECIDE is ranked (thresholds.md) and capped at 5; overflow is counted, not
shown. Pure Python — no LLM call, so the 6:30 job is deterministic and free.

Usage:
    python3 engine/render_daily.py [--date YYYY-MM-DD]
"""
import html
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import PRODUCERS, load_open  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUEUE, DAILY = ROOT / "queue", ROOT / "daily"
DECIDE_CAP = 5
ORDER = ("DECIDE", "APPROVE", "KNOW", "RAN")
BLURB = {
    "DECIDE": "Your judgment required. Ranked by consequence; top 5 shown.",
    "APPROVE": "Staged and ready. Approval = execute verbatim.",
    "KNOW": "No action needed. Awareness only.",
    "RAN": "Executed autonomously. Audit trail.",
}


def _by_type(items):
    buckets = {t: [] for t in ORDER}
    for it in items:
        buckets.get(it.type, buckets["KNOW"]).append(it)
    return buckets


def _held(decide):
    return decide[:DECIDE_CAP], max(0, len(decide) - DECIDE_CAP)


# ---------- markdown fallback ----------

def render_md(day, buckets):
    L = [f"# The Daily — {day}", ""]
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
            sev = f" · {it.severity}" if t == "DECIDE" else ""
            L.append(f"\n### {it.title}\n`{it.producer}` · {it.meta.get('autonomy_level_of_action','')}{sev}{dl}")
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
        L.append(f"---\n_Producers silent today: {', '.join(silent)}._")
    return "\n".join(L) + "\n"


# ---------- HTML ----------

_CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6b7280;--line:#e5e7eb;--card:#fafafa;
--decide:#b91c1c;--approve:#b45309;--know:#1d4ed8;--ran:#047857}
@media(prefers-color-scheme:dark){:root{--bg:#0e0f11;--fg:#e8e8e8;--mut:#9aa0a6;
--line:#26282c;--card:#16181b;--decide:#f87171;--approve:#fbbf24;--know:#60a5fa;--ran:#34d399}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:26px;margin:0 0 2px}.sub{color:var(--mut);margin:0 0 28px}
section{margin:0 0 28px}.sh{display:flex;align-items:baseline;gap:10px;
border-bottom:2px solid var(--line);padding-bottom:6px;margin-bottom:14px}
.sh h2{font-size:18px;margin:0;letter-spacing:.02em}.count{color:var(--mut);font-size:13px}
.blurb{color:var(--mut);font-size:13px;margin-left:auto}
.card{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--mut);
border-radius:8px;padding:14px 16px;margin:0 0 10px}
.t-DECIDE{border-left-color:var(--decide)}.t-APPROVE{border-left-color:var(--approve)}
.t-KNOW{border-left-color:var(--know)}.t-RAN{border-left-color:var(--ran)}
.ctitle{font-weight:600;font-size:15px}.meta{color:var(--mut);font-size:12px;margin:2px 0 8px;
display:flex;flex-wrap:wrap;gap:8px}.pill{background:var(--line);border-radius:20px;padding:1px 8px}
.sev-high{color:var(--decide);font-weight:600}
.cons{font-size:13px;color:var(--mut);border-left:2px solid var(--line);padding-left:10px;margin:6px 0}
.rec{font-size:14px;margin:8px 0 0}.rec b{color:var(--fg)}
.body{font-size:13px;color:var(--fg);margin:6px 0 0;white-space:pre-wrap}
pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;
overflow-x:auto;font-size:12px}.empty{color:var(--mut);font-style:italic}
.held{color:var(--mut);font-size:13px;margin-top:4px}
.foot{color:var(--mut);font-size:12px;border-top:1px solid var(--line);padding-top:14px;margin-top:28px}
.ran-line{font-size:13px}
"""


_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.DOTALL)


def _esc(s): return html.escape(str(s or ""))


def _staged(it):
    """The exact staged action for an APPROVE item: the fenced block if present,
    else the raw section text."""
    m = _FENCE.search(it.body)
    if m:
        return m.group(1).strip()
    return it.section("What I did about it") or it.section("What happened")


def _card(it, t):
    a = it.meta.get("autonomy_level_of_action", "")
    meta = [f'<span class="pill">{_esc(it.producer)}</span>',
            f'<span class="pill">{_esc(a)}</span>']
    if t == "DECIDE":
        cls = "sev-high" if it.severity == "high" else ""
        meta.append(f'<span class="{cls}">{_esc(it.severity)}</span>')
    if it.deadline:
        meta.append(f"due {_esc(it.deadline)}")
    parts = [f'<div class="card t-{t}">',
             f'<div class="ctitle">{_esc(it.title)}</div>',
             f'<div class="meta">{"".join(meta)}</div>',
             f'<div class="cons">consequence if ignored: {_esc(it.meta.get("consequence_if_ignored"))}</div>']
    if t == "DECIDE" and it.section("Recommendation"):
        parts.append(f'<div class="rec"><b>Recommendation:</b> {_esc(it.section("Recommendation"))}</div>')
    elif t == "APPROVE":
        staged = _staged(it)
        if staged:
            parts.append(f'<pre>{_esc(staged)}</pre>')
    elif t in ("KNOW", "RAN"):
        gist = it.section("What happened") or it.section("What I did about it")
        if gist:
            parts.append(f'<div class="body">{_esc(gist)}</div>')
    parts.append("</div>")
    return "".join(parts)


def render_html(day, buckets):
    reported = sorted({it.producer for b in buckets.values() for it in b})
    silent = sorted(PRODUCERS - set(reported))
    out = [f'<!doctype html><meta charset="utf-8"><title>The Daily — {day}</title>',
           f"<style>{_CSS}</style>", '<div class="wrap">',
           f"<h1>The Daily</h1><p class='sub'>{day} · clears in ≤10 min</p>"]
    for t in ORDER:
        items = buckets[t]
        shown, held = (_held(items) if t == "DECIDE" else (items, 0))
        out.append(f'<section><div class="sh"><h2>{t}</h2>'
                   f'<span class="count">{len(items)}</span>'
                   f'<span class="blurb">{BLURB[t]}</span></div>')
        if not shown:
            out.append('<p class="empty">— nothing —</p>')
        out += [_card(it, t) for it in shown]
        if t == "DECIDE" and held:
            out.append(f'<p class="held">+{held} more DECIDE held — '
                       f'resolve above to surface them.</p>')
        out.append("</section>")
    foot = f"Producers reporting: {', '.join(reported) or 'none'}."
    if silent:
        foot += f" Silent: {', '.join(silent)}."
    out.append(f'<div class="foot">{foot}</div></div>')
    return "".join(out)


def main(argv):
    day = date.today().isoformat()
    if "--date" in argv:
        day = argv[argv.index("--date") + 1]
        datetime.strptime(day, "%Y-%m-%d")  # validate
    items = load_open(QUEUE)
    buckets = _by_type(items)
    DAILY.mkdir(exist_ok=True)
    (DAILY / f"{day}.html").write_text(render_html(day, buckets), encoding="utf-8")
    (DAILY / f"{day}.md").write_text(render_md(day, buckets), encoding="utf-8")
    counts = " ".join(f"{t}:{len(buckets[t])}" for t in ORDER)
    print(f"rendered daily/{day}.html + .md  ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
