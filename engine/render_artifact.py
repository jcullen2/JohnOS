#!/usr/bin/env python3
"""Render the interactive Daily artifact (the review plane, engine/producers/
daily.md). Reads open /queue + state/stats.json and emits a self-contained HTML
body (no <html>/<head>/<body> — ready for the Artifact tool, also opens standalone).

Interactive: KPI strip, DECIDE/APPROVE action rows with ruling buttons, KNOW as
per-producer expanders, RAN one-liners, and a ruling tray that accumulates taps
into a copyable ruling list JC relays to Claude. It renders and records intent —
it SENDS NOTHING (standing-rule #0).

    python3 engine/render_artifact.py [--date YYYY-MM-DD] > daily/review.html
"""
import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import load_open  # noqa: E402
import stats as stats_mod  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.DOTALL)
E = lambda s: html.escape(str(s or ""))          # noqa: E731
ORDER = ("DECIDE", "APPROVE", "KNOW", "RAN")


def _staged(it):
    m = _FENCE.search(it.body)
    return m.group(1).strip() if m else ""


def _calnote(it):
    m = re.search(r"\*\*Calendar checked[^\n]*", it.body)
    return m.group(0).replace("**", "") if m else ""


def _collect(queue_dir):
    out = {t: [] for t in ORDER}
    for it in load_open(queue_dir):
        out.get(it.type, out["KNOW"]).append(it)
    return out


CSS = """
:root{
 --bg:#f4f6f9;--surface:#ffffff;--ink:#1a1d24;--mut:#5b6472;--faint:#8a93a2;
 --line:#e3e7ee;--accent:#3f5bd6;--accent-ink:#fff;
 --decide:#c8362c;--approve:#b3760c;--know:#2f6fc4;--ran:#1f8a5b;
 --chip:#eef1f6;
 --mono:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono",monospace;
 --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;}
@media(prefers-color-scheme:dark){:root{
 --bg:#0c0e12;--surface:#14171d;--ink:#e7eaef;--mut:#9aa2ad;--faint:#6b7280;
 --line:#242932;--accent:#7d92ff;--accent-ink:#0c0e12;
 --decide:#f0736a;--approve:#e6a935;--know:#5aa0f0;--ran:#3fbf87;--chip:#1c2029;}}
:root[data-theme="dark"]{
 --bg:#0c0e12;--surface:#14171d;--ink:#e7eaef;--mut:#9aa2ad;--faint:#6b7280;
 --line:#242932;--accent:#7d92ff;--accent-ink:#0c0e12;
 --decide:#f0736a;--approve:#e6a935;--know:#5aa0f0;--ran:#3fbf87;--chip:#1c2029;}
:root[data-theme="light"]{
 --bg:#f4f6f9;--surface:#ffffff;--ink:#1a1d24;--mut:#5b6472;--faint:#8a93a2;
 --line:#e3e7ee;--accent:#3f5bd6;--accent-ink:#fff;
 --decide:#c8362c;--approve:#b3760c;--know:#2f6fc4;--ran:#1f8a5b;--chip:#eef1f6;}
*{box-sizing:border-box}
.os{background:var(--bg);color:var(--ink);font-family:var(--sans);
 font-size:15px;line-height:1.5;min-height:100vh;padding:28px 18px 120px;
 -webkit-font-smoothing:antialiased}
.wrap{max-width:880px;margin:0 auto}
.head{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:6px}
.head h1{font-size:23px;margin:0;letter-spacing:-.01em}
.head .sub{color:var(--mut);font-size:13px}
.head .noscnd{color:var(--faint);font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:18px 0 26px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.kpi .n{font-family:var(--mono);font-size:22px;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.kpi .l{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.kpi .d{color:var(--faint);font-size:11px;margin-top:3px}
.kpi.alert .n{color:var(--decide)}
section{margin:0 0 22px}
.sh{display:flex;align-items:baseline;gap:9px;margin:0 0 11px}
.sh h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;margin:0}
.sh .c{font-family:var(--mono);color:var(--faint);font-size:12px}
.sh .bl{color:var(--faint);font-size:12px;margin-left:auto}
.row{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mut);
 border-radius:9px;padding:13px 15px;margin:0 0 9px}
.row.DECIDE{border-left-color:var(--decide)}.row.APPROVE{border-left-color:var(--approve)}
.row.done{opacity:.5}
.rtop{display:flex;align-items:flex-start;gap:9px}
.id{font-family:var(--mono);font-size:11px;color:var(--mut);border:1px solid var(--line);
 border-radius:5px;padding:1px 5px;white-space:nowrap}
.ttl{font-weight:600;flex:1}
.tags{display:flex;gap:7px;flex-wrap:wrap;margin:5px 0 0;font-size:12px;color:var(--mut)}
.tag{background:var(--chip);border-radius:20px;padding:1px 8px}
.sev-high{color:var(--decide);font-weight:600}
.cons{color:var(--mut);font-size:13px;border-left:2px solid var(--line);padding-left:9px;margin:8px 0 0}
.rec{font-size:14px;margin:8px 0 0}.rec b{color:var(--ink)}
.cal{display:inline-block;font-size:11.5px;color:var(--ran);background:color-mix(in srgb,var(--ran) 12%,transparent);
 border-radius:5px;padding:1px 7px;margin:8px 0 0}
details.draft{margin:9px 0 0}
details.draft>summary{cursor:pointer;font-size:12.5px;color:var(--accent);list-style:none}
details.draft>summary::-webkit-details-marker{display:none}
details.draft>summary::before{content:"▸ ";color:var(--faint)}
details.draft[open]>summary::before{content:"▾ "}
pre{background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:11px;
 margin:8px 0 0;overflow-x:auto;font-size:12.5px;font-family:var(--mono);white-space:pre-wrap}
.btns{display:flex;gap:7px;margin:11px 0 0;flex-wrap:wrap}
.btn{font:inherit;font-size:12.5px;cursor:pointer;border-radius:7px;padding:5px 12px;
 border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.btn:hover{border-color:var(--accent)}
.btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.btn.pri{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn.sel{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.grp{background:var(--surface);border:1px solid var(--line);border-radius:9px;margin:0 0 9px;
 border-left:3px solid var(--know)}
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
.tray{position:fixed;left:0;right:0;bottom:0;background:var(--surface);
 border-top:1px solid var(--line);padding:11px 18px;display:flex;gap:11px;align-items:center;flex-wrap:wrap}
.tray .lbl{font-size:12px;color:var(--mut)}
.tray .toks{display:flex;gap:6px;flex-wrap:wrap;flex:1;min-height:20px}
.tok{font-family:var(--mono);font-size:11px;background:var(--chip);border:1px solid var(--line);
 border-radius:5px;padding:1px 7px}
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
 else{rulings.set(id,verb);btn.classList.add('sel');row.classList.add('done');}
 paint();
}
function paint(){
 const t=document.getElementById('toks');t.innerHTML='';
 if(!rulings.size){t.innerHTML='<span class=empty>Tap Do-it / Approve / Skip on the items above…</span>';return;}
 for(const [id,v] of rulings){
  const s=document.createElement('span');s.className='tok';
  s.innerHTML=v+' '+id+' <span class=x data-id="'+id+'">✕</span>';
  t.appendChild(s);
 }
 t.querySelectorAll('.x').forEach(x=>x.onclick=()=>{
  const id=x.dataset.id;rulings.delete(id);
  const r=document.querySelector('.row[data-id="'+id+'"]');
  if(r){r.classList.remove('done');r.querySelectorAll('.btn').forEach(b=>b.classList.remove('sel'));}
  paint();});
}
function rulingList(){return [...rulings].map(([id,v])=>v+' '+id).join('\\n');}
function copyRulings(){
 const txt='Daily rulings — execute in-session (stage drafts, never send):\\n'+rulingList();
 navigator.clipboard.writeText(txt).then(()=>{
  const b=document.getElementById('copy');const o=b.textContent;b.textContent='Copied ✓';setTimeout(()=>b.textContent=o,1400);});
}
function closeOut(){
 if(!rulings.size){alert('No rulings yet. Tap the items first.');return;}
 copyRulings();
 alert('Rulings copied. Paste them back to Claude and it will:\\n• stage each Approve as a Superhuman draft (never send)\\n• act each Do-it within autonomy caps\\n• resolve ruled items to /archive and commit.');
}
document.addEventListener('DOMContentLoaded',paint);
"""


def _kpi(stats):
    q, p, f = stats["queue"], stats["producers"], stats["sourcing_funnel"]
    alert = " alert" if q["decide_oldest_age_days"] > 2 else ""
    tiles = [
        (q["decide_open"], "DECIDE open", f"oldest {q['decide_oldest_age_days']}d", alert),
        (q["approve_staged"], "APPROVE staged", "ready to send by hand", ""),
        (q["due_today"], "Due today", "", " alert" if q["due_today"] else ""),
        (f"{f['this_week']}", "Sourcing this wk", f"vs {f['last_week']} last", ""),
        (f"{p['n']}/{p['m']}", "Producers", "silent: " + (", ".join(p["silent"]) or "none"), ""),
    ]
    out = ['<div class="kpis">']
    for n, l, d, a in tiles:
        out.append(f'<div class="kpi{a}"><div class="n">{E(n)}</div>'
                   f'<div class="l">{E(l)}</div><div class="d">{E(d)}</div></div>')
    out.append("</div>")
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


def _approve(it):
    dl = f'<span class="tag">due {E(it.deadline)}</span>' if it.deadline else ""
    cal = f'<div class="cal">✓ {E(it.calnote_text)}</div>' if getattr(it, "calnote_text", "") else ""
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


def render(day, queue_dir=ROOT / "queue"):
    stats = stats_mod.build()
    buckets = _collect(queue_dir)
    for it in buckets["APPROVE"]:
        it.calnote_text = _calnote(it)
    p = ["<style>", CSS, "</style>", '<div class="os"><div class="wrap">',
         f'<div class="head"><h1>The Daily</h1>'
         f'<span class="sub">{day} · morning · clears in ≤10 min</span>'
         f'<span class="noscnd">sends nothing · drafts stage only</span></div>',
         _kpi(stats)]

    p.append('<section><div class="sh"><h2>Decide</h2>'
             f'<span class="c">{len(buckets["DECIDE"])}</span>'
             '<span class="bl">your judgment · ranked</span></div>')
    p += [_decide(it) for it in buckets["DECIDE"][:5]] or ['<p class="empty">nothing</p>']
    p.append("</section>")

    p.append('<section><div class="sh"><h2>Approve</h2>'
             f'<span class="c">{len(buckets["APPROVE"])}</span>'
             '<span class="bl">approval stages the draft — never sends</span></div>')
    p += [_approve(it) for it in buckets["APPROVE"]] or ['<p class="empty">nothing</p>']
    p.append("</section>")

    p.append('<section><div class="sh"><h2>Know</h2>'
             f'<span class="c">{len(buckets["KNOW"])}</span>'
             '<span class="bl">awareness · grouped</span></div>')
    p.append(_know_groups(buckets["KNOW"]) or '<p class="empty">nothing</p>')
    p.append("</section>")

    p.append('<section><div class="sh"><h2>Ran</h2>'
             f'<span class="c">{len(buckets["RAN"])}</span>'
             '<span class="bl">autonomous · audit</span></div>')
    p += [f'<div class="ran"><span class="id">{E(it.id)}</span>{E(it.title)}</div>'
          for it in buckets["RAN"]] or ['<p class="empty">nothing</p>']
    p.append("</section>")

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
