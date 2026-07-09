#!/usr/bin/env python3
"""Render the interactive Daily artifact (the review plane, engine/producers/
daily.md). Reads open /queue, state/stats.json, state/calendar-week.json, and
state/sourcing-prefs.json; emits a self-contained HTML body (no <html>/<head>/
<body> — ready for the Artifact tool, also opens standalone).

Sections: your week (calendar) · DECIDE · SOURCING (first-class, with feedback) ·
APPROVE · KNOW · RAN, plus a ruling tray. It renders and records intent — it
SENDS NOTHING (standing-rule #0). Rulings feed the living loops (feedback-loops.md).

    python3 engine/render_artifact.py [--date YYYY-MM-DD] > daily/review.html
"""
import argparse
import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import load_open  # noqa: E402
import stats as stats_mod  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.DOTALL)
E = lambda s: html.escape(str(s or ""))          # noqa: E731
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
CAL_START, CAL_END = 8 * 60, 19 * 60             # 8:00–19:00 grid


def _staged(it):
    m = _FENCE.search(it.body)
    return m.group(1).strip() if m else ""


def _calnote(it):
    m = re.search(r"\*\*Calendar checked[^\n]*", it.body)
    return m.group(0).replace("**", "") if m else ""


def _collect(queue_dir):
    b = {"DECIDE": [], "SOURCING": [], "APPROVE": [], "KNOW": [], "RAN": []}
    for it in load_open(queue_dir):
        if it.producer == "sourcing" and it.type == "KNOW":
            b["SOURCING"].append(it)
        else:
            b.get(it.type, b["KNOW"]).append(it)
    return b


def _load(name, default):
    p = STATE / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


# ---------------- CSS ----------------
CSS = """
:root{
 --bg:#f4f6f9;--surface:#ffffff;--ink:#1a1d24;--mut:#5b6472;--faint:#8a93a2;
 --line:#e3e7ee;--accent:#3f5bd6;--accent-ink:#fff;
 --decide:#c8362c;--approve:#b3760c;--know:#2f6fc4;--ran:#1f8a5b;--source:#7a3fd6;
 --chip:#eef1f6;--today:#eef2ff;
 --mono:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono",monospace;
 --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;}
:root[data-theme="dark"],
:root:not([data-theme="light"]){}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --bg:#0c0e12;--surface:#14171d;--ink:#e7eaef;--mut:#9aa2ad;--faint:#6b7280;
 --line:#242932;--accent:#7d92ff;--accent-ink:#0c0e12;
 --decide:#f0736a;--approve:#e6a935;--know:#5aa0f0;--ran:#3fbf87;--source:#b18bff;
 --chip:#1c2029;--today:#1a1f33;}}
:root[data-theme="dark"]{
 --bg:#0c0e12;--surface:#14171d;--ink:#e7eaef;--mut:#9aa2ad;--faint:#6b7280;
 --line:#242932;--accent:#7d92ff;--accent-ink:#0c0e12;
 --decide:#f0736a;--approve:#e6a935;--know:#5aa0f0;--ran:#3fbf87;--source:#b18bff;
 --chip:#1c2029;--today:#1a1f33;}
*{box-sizing:border-box}
.os{background:var(--bg);color:var(--ink);font-family:var(--sans);
 font-size:15px;line-height:1.5;min-height:100vh;padding:26px 18px 118px;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto}
.head{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:6px}
.head h1{font-size:23px;margin:0;letter-spacing:-.01em}
.head .sub{color:var(--mut);font-size:13px}
.head .noscnd{color:var(--faint);font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:16px 0 22px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.kpi .n{font-family:var(--mono);font-size:22px;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi .l{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.kpi .d{color:var(--faint);font-size:11px;margin-top:3px}
.kpi.alert .n{color:var(--decide)}
.sh{display:flex;align-items:baseline;gap:9px;margin:22px 0 11px}
.sh h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;margin:0}
.sh .c{font-family:var(--mono);color:var(--faint);font-size:12px}
.sh .bl{color:var(--faint);font-size:12px;margin-left:auto}
/* calendar */
.cal{background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:12px;overflow-x:auto}
.calgrid{display:grid;grid-template-columns:38px repeat(7,minmax(84px,1fr));min-width:640px}
.calhh{grid-column:1;position:relative}
.calhh .hr{position:absolute;right:5px;font-family:var(--mono);font-size:9.5px;color:var(--faint);transform:translateY(-5px)}
.calday{position:relative;border-left:1px solid var(--line);height:340px}
.calday.today{background:var(--today)}
.caldh{position:sticky;top:0;text-align:center;font-size:11px;padding:2px 0 6px}
.caldh .dn{color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
.caldh .dd{font-family:var(--mono);font-size:14px}
.caldh .today-dot{color:var(--accent);font-weight:700}
.calline{position:absolute;left:0;right:0;border-top:1px solid var(--line);opacity:.55}
.ev{position:absolute;left:3px;right:3px;border-radius:6px;padding:3px 5px;overflow:hidden;
 font-size:10.5px;line-height:1.25;background:color-mix(in srgb,var(--accent) 15%,var(--surface));
 border-left:2px solid var(--accent);color:var(--ink)}
.ev.detroit{background:color-mix(in srgb,var(--ran) 15%,var(--surface));border-left-color:var(--ran)}
.ev .et{font-family:var(--mono);font-size:9px;color:var(--mut)}
.cal .none{color:var(--faint);font-size:12px;font-style:italic;padding:6px 2px}
/* rows */
.row{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mut);
 border-radius:9px;padding:13px 15px;margin:0 0 9px}
.row.DECIDE{border-left-color:var(--decide)}.row.APPROVE{border-left-color:var(--approve)}
.row.SOURCING{border-left-color:var(--source)}
.row.done{opacity:.5}
.rtop{display:flex;align-items:flex-start;gap:9px}
.id{font-family:var(--mono);font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:5px;padding:1px 5px;white-space:nowrap}
.ttl{font-weight:600;flex:1}
.tags{display:flex;gap:7px;flex-wrap:wrap;margin:5px 0 0;font-size:12px;color:var(--mut)}
.tag{background:var(--chip);border-radius:20px;padding:1px 8px}
.tag.thesis{background:color-mix(in srgb,var(--source) 16%,transparent);color:var(--source)}
.tag.new{background:color-mix(in srgb,var(--ran) 16%,transparent);color:var(--ran)}
.tag.crm{background:var(--chip);color:var(--mut)}
.sev-high{color:var(--decide);font-weight:600}
.cons{color:var(--mut);font-size:13px;border-left:2px solid var(--line);padding-left:9px;margin:8px 0 0}
.rec{font-size:14px;margin:8px 0 0}.rec b{color:var(--ink)}
.gist{font-size:13px;color:var(--mut);margin:7px 0 0}
.cal-ok{display:inline-block;font-size:11.5px;color:var(--ran);background:color-mix(in srgb,var(--ran) 12%,transparent);border-radius:5px;padding:1px 7px;margin:8px 0 0}
details.draft{margin:9px 0 0}
details.draft>summary{cursor:pointer;font-size:12.5px;color:var(--accent);list-style:none}
details.draft>summary::-webkit-details-marker{display:none}
details.draft>summary::before{content:"▸ ";color:var(--faint)}
details.draft[open]>summary::before{content:"▾ "}
pre{background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:11px;margin:8px 0 0;
 overflow-x:auto;font-size:12.5px;font-family:var(--mono);white-space:pre-wrap}
.btns{display:flex;gap:7px;margin:11px 0 0;flex-wrap:wrap}
.btn{font:inherit;font-size:12.5px;cursor:pointer;border-radius:7px;padding:5px 12px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.btn:hover{border-color:var(--accent)}
.btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.btn.pri{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn.good{border-color:color-mix(in srgb,var(--ran) 50%,var(--line))}
.btn.sel{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.grp{background:var(--surface);border:1px solid var(--line);border-radius:9px;margin:0 0 9px;border-left:3px solid var(--know)}
.grp>summary{cursor:pointer;padding:11px 15px;font-weight:600;list-style:none;display:flex;gap:9px;align-items:center}
.grp>summary::-webkit-details-marker{display:none}
.grp>summary::before{content:"▸";color:var(--faint)}
.grp[open]>summary::before{content:"▾"}
.grp .gc{font-family:var(--mono);color:var(--faint);font-size:12px;margin-left:auto}
.know{padding:0 15px 4px 15px}
.know .k{border-top:1px solid var(--line);padding:10px 0}
.know .k .kt{font-weight:600;font-size:14px}
.know .k .kg{color:var(--mut);font-size:13px;margin-top:3px;white-space:pre-wrap}
.ran{font-size:13px;color:var(--mut);padding:5px 0;border-bottom:1px solid var(--line)}
.ran .id{margin-right:7px}
.tray{position:fixed;left:0;right:0;bottom:0;background:var(--surface);border-top:1px solid var(--line);
 padding:11px 18px;display:flex;gap:11px;align-items:center;flex-wrap:wrap}
.tray .lbl{font-size:12px;color:var(--mut)}
.tray .toks{display:flex;gap:6px;flex-wrap:wrap;flex:1;min-height:20px}
.tok{font-family:var(--mono);font-size:11px;background:var(--chip);border:1px solid var(--line);border-radius:5px;padding:1px 7px}
.tok .x{cursor:pointer;color:var(--faint);margin-left:4px}
.empty{color:var(--faint);font-style:italic;font-size:13px}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
const rulings=new Map();
function ruling(id,verb,btn){
 const row=btn.closest('.row');
 row.querySelectorAll('.btn').forEach(b=>b.classList.remove('sel'));
 if(rulings.get(id)===verb){rulings.delete(id);row.classList.remove('done');}
 else{rulings.set(id,verb);btn.classList.add('sel');
  if(!['MORE','PASS','MEET','WATCH'].includes(verb))row.classList.add('done');}
 paint();
}
function paint(){
 const t=document.getElementById('toks');t.innerHTML='';
 if(!rulings.size){t.innerHTML='<span class=empty>Tap a ruling on any item above…</span>';return;}
 for(const [id,v] of rulings){
  const s=document.createElement('span');s.className='tok';
  s.innerHTML=v+' '+id+' <span class=x data-id="'+id+'">✕</span>';t.appendChild(s);}
 t.querySelectorAll('.x').forEach(x=>x.onclick=()=>{
  const id=x.dataset.id;rulings.delete(id);
  const r=document.querySelector('.row[data-id="'+id+'"]');
  if(r){r.classList.remove('done');r.querySelectorAll('.btn').forEach(b=>b.classList.remove('sel'));}
  paint();});
}
function rulingList(){return [...rulings].map(([id,v])=>v+' '+id).join('\\n');}
function copyRulings(){
 const txt='Daily rulings — execute in-session (stage drafts, never send; apply sourcing feedback to prefs):\\n'+rulingList();
 navigator.clipboard.writeText(txt).then(()=>{const b=document.getElementById('copy');const o=b.textContent;b.textContent='Copied ✓';setTimeout(()=>b.textContent=o,1400);});
}
function closeOut(){
 if(!rulings.size){alert('No rulings yet. Tap the items first.');return;}
 copyRulings();
 alert('Rulings copied. Paste them back to Claude to:\\n• stage each Approve as a Superhuman draft (never send)\\n• act each Do-it within autonomy caps\\n• fold sourcing More/Pass/Meet/Watch into sourcing-prefs\\n• resolve ruled items to /archive and commit.');
}
document.addEventListener('DOMContentLoaded',paint);
"""


# ---------------- components ----------------
def _kpi(stats):
    q, p, f = stats["queue"], stats["producers"], stats["sourcing_funnel"]
    tiles = [
        (q["decide_open"], "DECIDE open", f"oldest {q['decide_oldest_age_days']}d",
         " alert" if q["decide_oldest_age_days"] > 2 else ""),
        (q["approve_staged"], "APPROVE staged", "send by hand", ""),
        (q["due_today"], "Due today", "", " alert" if q["due_today"] else ""),
        (f["this_week"], "Sourcing this wk", f"vs {f['last_week']} last", ""),
        (f"{p['n']}/{p['m']}", "Producers", "silent: " + (", ".join(p["silent"]) or "none"), ""),
    ]
    out = ['<div class="kpis">']
    for n, l, d, a in tiles:
        out.append(f'<div class="kpi{a}"><div class="n">{E(n)}</div>'
                   f'<div class="l">{E(l)}</div><div class="d">{E(d)}</div></div>')
    return "".join(out) + "</div>"


def _mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _calendar(week, today):
    ev_by_day = {}
    for e in week.get("events", []):
        ev_by_day.setdefault(e["day"], []).append(e)
    monday = date.fromisoformat(week["week_of"])
    span = CAL_END - CAL_START
    out = ['<div class="cal"><div class="calgrid">']
    # hour gutter
    out.append('<div class="calhh">')
    for h in range(8, 20):
        top = (h * 60 - CAL_START) / span * 100
        out.append(f'<div class="hr" style="position:absolute;top:{top:.1f}%">{h}:00</div>')
    out.append('</div>')
    for i, dn in enumerate(DAYS):
        d = date.fromordinal(monday.toordinal() + i)
        iso = d.isoformat()
        is_today = iso == today
        head = (f'<div class="caldh"><div class="dn">{dn}</div>'
                f'<div class="dd {"today-dot" if is_today else ""}">{d.day}</div></div>')
        lines = "".join(
            f'<div class="calline" style="top:{(h*60-CAL_START)/span*100:.1f}%"></div>'
            for h in range(9, 20))
        blocks = []
        for e in ev_by_day.get(iso, []):
            s, en = _mins(e["start"]), _mins(e["end"])
            top = max(0, (s - CAL_START) / span * 100)
            hgt = max(4, (en - s) / span * 100)
            kind = " detroit" if e.get("kind") == "detroit" else ""
            blocks.append(
                f'<div class="ev{kind}" style="top:{top:.1f}%;height:{hgt:.1f}%">'
                f'<div class="et">{E(e["start"])}</div>{E(e["title"])}</div>')
        out.append(f'<div class="calday{" today" if is_today else ""}">'
                   f'{head}{lines}{"".join(blocks)}</div>')
    out.append('</div></div>')
    return "".join(out)


def _decide(it):
    sev = "sev-high" if it.severity == "high" else ""
    dl = f'<span class="tag">due {E(it.deadline)}</span>' if it.deadline else ""
    return (f'<div class="row DECIDE" data-id="{E(it.id)}"><div class="rtop">'
            f'<span class="id">{E(it.id)}</span><span class="ttl">{E(it.title)}</span></div>'
            f'<div class="tags"><span class="tag">{E(it.producer)}</span>'
            f'<span class="{sev}">{E(it.severity)}</span>{dl}</div>'
            f'<div class="cons">{E(it.meta.get("consequence_if_ignored"))}</div>'
            f'<div class="rec"><b>Recommendation:</b> {E(it.section("Recommendation"))}</div>'
            f'<div class="btns"><button class="btn pri" onclick="ruling(\'{it.id}\',\'DO-IT\',this)">Do-it</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'DISCUSS\',this)">Discuss</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'SKIP\',this)">Skip</button></div></div>')


def _sourcing(it):
    m = it.meta
    aff = (m.get("affinity") or "").lower()
    aff_tag = (f'<span class="tag new">net-new</span>' if "net-new" in aff
               else f'<span class="tag crm">in-CRM</span>' if aff else "")
    meta = f'{E(m.get("round",""))}' + (f' · {E(m.get("lead"))}' if m.get("lead") else "")
    return (f'<div class="row SOURCING" data-id="{E(it.id)}"><div class="rtop">'
            f'<span class="id">{E(it.id)}</span><span class="ttl">{E(it.title)}</span></div>'
            f'<div class="tags"><span class="tag thesis">{E(m.get("thesis","—"))}</span>'
            f'{aff_tag}<span class="tag">{E(meta)}</span></div>'
            f'<div class="gist">{E(it.section("What happened"))}</div>'
            f'<div class="btns"><button class="btn good" onclick="ruling(\'{it.id}\',\'MORE\',this)">More like this</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'MEET\',this)">Get me in</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'WATCH\',this)">Watch</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'PASS\',this)">Pass</button></div></div>')


def _approve(it):
    dl = f'<span class="tag">due {E(it.deadline)}</span>' if it.deadline else ""
    cal = f'<div class="cal-ok">✓ {E(_calnote(it))}</div>' if _calnote(it) else ""
    staged = _staged(it)
    draft = (f'<details class="draft"><summary>staged draft</summary>'
             f'<pre>{E(staged)}</pre></details>') if staged else ""
    return (f'<div class="row APPROVE" data-id="{E(it.id)}"><div class="rtop">'
            f'<span class="id">{E(it.id)}</span><span class="ttl">{E(it.title)}</span></div>'
            f'<div class="tags"><span class="tag">{E(it.producer)}</span>{dl}</div>'
            f'{cal}{draft}'
            f'<div class="btns"><button class="btn pri" onclick="ruling(\'{it.id}\',\'APPROVE\',this)">Approve</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'EDIT\',this)">Edit</button>'
            f'<button class="btn" onclick="ruling(\'{it.id}\',\'SKIP\',this)">Skip</button></div></div>')


def _know_groups(items):
    by = {}
    for it in items:
        by.setdefault(it.producer, []).append(it)
    out = []
    for prod, its in by.items():
        rows = "".join(
            f'<div class="k"><div class="kt">{E(i.title)}</div>'
            f'<div class="kg">{E(i.section("What happened") or i.section("What I did about it"))}</div></div>'
            for i in its)
        out.append(f'<details class="grp"><summary>{E(prod)}'
                   f'<span class="gc">{len(its)}</span></summary>'
                   f'<div class="know">{rows}</div></details>')
    return "".join(out)


def _section(title, count, blurb):
    return (f'<div class="sh"><h2>{title}</h2><span class="c">{count}</span>'
            f'<span class="bl">{blurb}</span></div>')


def render(day, queue_dir=ROOT / "queue"):
    stats = stats_mod.build()
    b = _collect(queue_dir)
    week = _load("calendar-week.json", {"week_of": day, "events": []})

    p = [f"<title>The Daily — {E(day)}</title>", "<style>", CSS, "</style>",
         '<div class="os"><div class="wrap">',
         f'<div class="head"><h1>The Daily</h1>'
         f'<span class="sub">{E(day)} · morning · clears in ≤10 min</span>'
         f'<span class="noscnd">sends nothing · drafts stage only</span></div>',
         _kpi(stats)]

    p.append(_section("Your week", "", "live from Google Calendar"))
    p.append(_calendar(week, day))

    p.append(_section("Decide", len(b["DECIDE"]), "your judgment · ranked"))
    p += [_decide(it) for it in b["DECIDE"][:5]] or ['<p class="empty">nothing</p>']

    p.append(_section("Sourcing", len(b["SOURCING"]), "the engine · tell it what you want more of"))
    p += [_sourcing(it) for it in b["SOURCING"]] or ['<p class="empty">no candidates tonight</p>']

    p.append(_section("Approve", len(b["APPROVE"]), "approval stages the draft — never sends"))
    p += [_approve(it) for it in b["APPROVE"]] or ['<p class="empty">nothing</p>']

    p.append(_section("Know", len(b["KNOW"]), "awareness · grouped"))
    p.append(_know_groups(b["KNOW"]) or '<p class="empty">nothing</p>')

    p.append(_section("Ran", len(b["RAN"]), "autonomous · audit"))
    p += [f'<div class="ran"><span class="id">{E(it.id)}</span>{E(it.title)}</div>'
          for it in b["RAN"]] or ['<p class="empty">nothing</p>']

    p.append('</div></div>')
    p.append('<div class="tray"><span class="lbl">Rulings</span>'
             '<div class="toks" id="toks"></div>'
             '<button class="btn" id="copy" onclick="copyRulings()">Copy rulings</button>'
             '<button class="btn pri" onclick="closeOut()">Close out the day</button></div>')
    p.append(f"<script>{JS}</script>")
    return "".join(p)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--queue", type=Path, default=ROOT / "queue")
    a = ap.parse_args(argv[1:])
    sys.stdout.write(render(a.date, a.queue))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
