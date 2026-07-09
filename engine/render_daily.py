#!/usr/bin/env python3
"""The Daily renderer (FOUNDING_SPEC §6).

Reads open /queue items and renders one self-contained HTML artifact plus a
markdown fallback into /daily. Section order is fixed: DECIDE → APPROVE → KNOW →
RAN. DECIDE is ranked (thresholds.md) and capped at 5; overflow is counted, not
shown. Pure Python — no LLM call, so the render is deterministic and free.

Editions:
  morning (default)  full Daily → /daily/<date>.{html,md}          (7:00 job)
  evening (--since)  delta only → /daily/<date>-pm.{html,md}       (17:00 job)
    shows items created/changed since the cutoff, plus anything crossing the
    urgency threshold (thresholds.md).

Usage:
  python3 engine/render_daily.py [--date YYYY-MM-DD] [--queue DIR] [--out DIR]
  python3 engine/render_daily.py --since 07:00        # evening delta
  python3 engine/render_daily.py --open --email me@x  # deliver (see env vars)
"""
import argparse
import html
import os
import re
import smtplib
import sys
import webbrowser
from datetime import date, datetime
from email.message import EmailMessage
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


def _select(items, since_ts):
    """Morning: all open items. Evening (since_ts set): only items changed since
    the cutoff, plus anything crossing the urgency threshold."""
    if since_ts is None:
        return items
    return [it for it in items
            if it.changed_at >= since_ts or it.crosses_urgency()]


# ---------- markdown fallback ----------

def render_md(day, buckets, edition="morning", since=None):
    head = f"# The Daily — {day}"
    if edition == "evening":
        head += f"  ·  evening edition (Δ since {since})"
    L = [head, ""]
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
            sev = f" · {it.severity}" if t == "DECIDE" else ""
            L.append(f"\n### [{it.id}] {it.title}\n`{it.producer}` · "
                     f"{it.meta.get('autonomy_level_of_action','')}{sev}{dl}")
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
.note{color:var(--mut);font-style:italic;margin:0 0 20px}
section{margin:0 0 28px}.sh{display:flex;align-items:baseline;gap:10px;
border-bottom:2px solid var(--line);padding-bottom:6px;margin-bottom:14px}
.sh h2{font-size:18px;margin:0;letter-spacing:.02em}.count{color:var(--mut);font-size:13px}
.blurb{color:var(--mut);font-size:13px;margin-left:auto}
.card{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--mut);
border-radius:8px;padding:14px 16px;margin:0 0 10px}
.t-DECIDE{border-left-color:var(--decide)}.t-APPROVE{border-left-color:var(--approve)}
.t-KNOW{border-left-color:var(--know)}.t-RAN{border-left-color:var(--ran)}
.ctitle{font-weight:600;font-size:15px}
.id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;
color:var(--mut);border:1px solid var(--line);border-radius:5px;padding:0 5px;margin-right:6px}
.meta{color:var(--mut);font-size:12px;margin:2px 0 8px;
display:flex;flex-wrap:wrap;gap:8px}.pill{background:var(--line);border-radius:20px;padding:1px 8px}
.sev-high{color:var(--decide);font-weight:600}
.cons{font-size:13px;color:var(--mut);border-left:2px solid var(--line);padding-left:10px;margin:6px 0}
.rec{font-size:14px;margin:8px 0 0}.rec b{color:var(--fg)}
.body{font-size:13px;color:var(--fg);margin:6px 0 0;white-space:pre-wrap}
pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;
overflow-x:auto;font-size:12px}.empty{color:var(--mut);font-style:italic}
.held{color:var(--mut);font-size:13px;margin-top:4px}
.foot{color:var(--mut);font-size:12px;border-top:1px solid var(--line);padding-top:14px;margin-top:28px}
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
             f'<div class="ctitle"><span class="id">{_esc(it.id)}</span>{_esc(it.title)}</div>',
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


def render_html(day, buckets, edition="morning", since=None):
    reported = sorted({it.producer for b in buckets.values() for it in b})
    silent = sorted(PRODUCERS - set(reported))
    title = f"The Daily — {day}" + (" (evening)" if edition == "evening" else "")
    sub = (f"{day} · evening edition · Δ since {since}" if edition == "evening"
           else f"{day} · clears in ≤10 min")
    out = [f'<!doctype html><meta charset="utf-8"><title>{title}</title>',
           f"<style>{_CSS}</style>", '<div class="wrap">',
           f"<h1>The Daily</h1><p class='sub'>{sub}</p>"]
    if edition == "evening" and sum(len(v) for v in buckets.values()) == 0:
        out.append(f'<p class="note">No changes since {since}. '
                   f'Nothing crossed the urgency threshold.</p>')
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


def render(day, queue_dir, out_dir, since_ts=None, since_label=None):
    """Render both artifacts. since_ts set → evening delta (suffix -pm)."""
    edition = "evening" if since_ts is not None else "morning"
    items = _select(load_open(queue_dir), since_ts)
    buckets = _by_type(items)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-pm" if edition == "evening" else ""
    base = out_dir / f"{day}{suffix}"
    base.with_suffix(".html").write_text(
        render_html(day, buckets, edition, since_label), encoding="utf-8")
    base.with_suffix(".md").write_text(
        render_md(day, buckets, edition, since_label), encoding="utf-8")
    return buckets, base


# ---------- delivery (built now; fired only when scheduled — GATE 3) ----------

def _parse_since(s):
    """'HH:MM' → today at that time; else ISO datetime. Returns (epoch, label)."""
    if re.fullmatch(r"\d{1,2}:\d{2}", s):
        t = datetime.strptime(s, "%H:%M").time()
        dt = datetime.combine(date.today(), t)
    else:
        dt = datetime.fromisoformat(s)
    return dt.timestamp(), dt.strftime("%H:%M")


def open_in_browser(html_path):
    webbrowser.open(f"file://{html_path.resolve()}")


def email_to(addr, subject, html_path):
    """Email the Daily to JC's own address (the L2 carve-out — autonomy.md).
    SMTP config via env: SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASS,
    DAILY_FROM. Unconfigured → skip with a notice, never crash the render."""
    hostname = os.environ.get("SMTP_HOST")
    if not hostname:
        print(f"  [email skipped: SMTP_HOST unset — would send '{subject}' to {addr}]")
        return False
    msg = EmailMessage()
    msg["Subject"], msg["To"] = subject, addr
    msg["From"] = os.environ.get("DAILY_FROM", addr)
    body = html_path.read_text(encoding="utf-8")
    msg.set_content("The Daily is an HTML email; enable HTML to view.")
    msg.add_alternative(body, subtype="html")
    with smtplib.SMTP(hostname, int(os.environ.get("SMTP_PORT", "587"))) as s:
        s.starttls()
        if os.environ.get("SMTP_USER"):
            s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASS", ""))
        s.send_message(msg)
    print(f"  [emailed '{subject}' to {addr}]")
    return True


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--queue", type=Path, default=QUEUE)
    ap.add_argument("--out", type=Path, default=DAILY)
    ap.add_argument("--since", help="evening delta cutoff: 'HH:MM' or ISO datetime")
    ap.add_argument("--open", action="store_true", help="open the HTML in a browser")
    ap.add_argument("--email", metavar="ADDR", help="email the Daily to an address")
    a = ap.parse_args(argv[1:])
    datetime.strptime(a.date, "%Y-%m-%d")  # validate

    since_ts, since_label = (_parse_since(a.since) if a.since else (None, None))
    buckets, base = render(a.date, a.queue, a.out, since_ts, since_label)

    edition = "evening" if since_ts is not None else "morning"
    counts = " ".join(f"{t}:{len(buckets[t])}" for t in ORDER)
    print(f"rendered {base}.html + .md  [{edition}]  ({counts})")
    if a.open:
        open_in_browser(base.with_suffix(".html"))
    if a.email:
        subj = f"The Daily — {a.date}" + (" (evening)" if edition == "evening" else "")
        email_to(a.email, subj, base.with_suffix(".html"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
