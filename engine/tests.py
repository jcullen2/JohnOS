#!/usr/bin/env python3
"""Engine self-tests. Stdlib only — no pytest. Run: python3 engine/tests.py

Covers the invariants the whole system leans on: schema validation catches every
error class, DECIDE ranking is correct, qwrite round-trips through the validator,
and the renderer produces both artifacts in the fixed section order.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import qitem  # noqa: E402
import qwrite  # noqa: E402
import render_daily as rd  # noqa: E402

FIX = HERE / "fixtures" / "queue"
_n = [0, 0]


def check(cond, msg):
    _n[0] += 1
    if not cond:
        _n[1] += 1
        print(f"FAIL: {msg}")
    else:
        print(f"ok  : {msg}")


def test_fixtures_valid():
    items = [qitem.load(p) for p in FIX.glob("*.md")]
    check(len(items) == 8, f"8 fixtures present (got {len(items)})")
    for it in items:
        errs, _ = qitem.validate(it)
        check(not errs, f"{it.path.name} validates ({errs})")


def test_ranking():
    items = qitem.load_open(FIX)
    decide = [i for i in items if i.type == "DECIDE"]
    sev = [i.severity for i in decide]
    check(sev == sorted(sev, key=lambda s: -qitem.SEVERITY[s]),
          f"DECIDE ordered by severity desc ({sev})")


def test_validator_catches_errors():
    bad = ("---\nproducer: bogus\ntype: DECIDE\ntitle: x\n"
           "consequence_if_ignored:\ndeadline: soon\n"
           "autonomy_level_of_action: L9\nstatus: open\n---\n\n## What happened\nx\n")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "bad.md"
        p.write_text(bad)
        errs, _ = qitem.validate(qitem.load(p))
    for token in ("producer", "autonomy", "deadline", "consequence", "Recommendation"):
        check(any(token in e for e in errs), f"validator flags {token}")


def test_qwrite_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        path = qwrite.write_item(
            d, producer="inbound", type="DECIDE", slug="test-item",
            title="A test decision", consequence_if_ignored="something slips",
            autonomy_level_of_action="L1", deadline="2026-07-10", severity="high",
            what_happened="x", recommendation="do the thing", what_i_need="a yes")
        errs, _ = qitem.validate(qitem.load(path))
        check(not errs, f"qwrite output validates ({errs})")
        check(path.name.endswith("-inbound-test-item.md"),
              f"canonical filename ({path.name})")
    try:
        qwrite.write_item(d, producer="inbound", type="DECIDE", slug="x",
                          title="no rec", consequence_if_ignored="y",
                          autonomy_level_of_action="L1")
        check(False, "qwrite rejects invalid item")
    except ValueError:
        check(True, "qwrite rejects invalid item")


def test_render():
    with tempfile.TemporaryDirectory() as d:
        rd.render("2026-07-09", FIX, Path(d))
        md = (Path(d) / "2026-07-09.md").read_text()
    check(md.index("DECIDE") < md.index("APPROVE") < md.index("KNOW")
          < md.index("RAN"), "section order DECIDE→APPROVE→KNOW→RAN")
    check("Appreciate" in md, "APPROVE staged action rendered verbatim")
    check(md.startswith("# The Daily"), "markdown audit produced")
    # consequence line only on DECIDE/APPROVE, never KNOW/RAN
    know = md[md.index("## KNOW"):]
    check("consequence if ignored" not in know, "consequence suppressed on KNOW/RAN")
    check("<html" not in md and "<pre>" not in md, "no HTML emitted (md only)")


def test_no_send_surface():
    src = (HERE / "render_daily.py").read_text()
    check("smtplib" not in src and "webbrowser" not in src and "--email" not in src,
          "renderer has no send/email/open surface (standing-rule #0)")


def test_stats():
    import stats
    s = stats.build()
    check("decide_open" in s["queue"] and "thesis_counters" in s,
          "stats.json has KPI fields")


if __name__ == "__main__":
    for fn in [test_fixtures_valid, test_ranking, test_validator_catches_errors,
               test_qwrite_roundtrip, test_render, test_no_send_surface, test_stats]:
        fn()
    print(f"\n{_n[0]} checks, {_n[1]} failed")
    sys.exit(1 if _n[1] else 0)
