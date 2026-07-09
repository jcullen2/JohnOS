#!/usr/bin/env python3
"""Thesis signal counters (spec §5, the `thesis` mechanism). sourcing / news /
policy / intake bump a thesis when they surface evidence for it; when a counter
reaches its threshold the thesis producer fires a synthesis-session DECIDE.
Stdlib only. State: /state/theses.json.

    python3 engine/signals.py bump maritime-autonomy --n 1 --source sourcing
    python3 engine/signals.py status
    python3 engine/signals.py crossings        # names at/over threshold, one per line
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / "state" / "theses.json"


def load():
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(d):
    d["updated"] = date.today().isoformat()
    STATE.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")


def bump(thesis, n=1, source=None):
    d = load()
    t = d["theses"].get(thesis)
    if t is None:
        raise KeyError(f"unknown thesis '{thesis}'; known: {sorted(d['theses'])}")
    t["signals"] += n
    t["last_signal"] = date.today().isoformat()
    if source:
        t["last_source"] = source
    save(d)
    return t


def crossings(d=None):
    d = d or load()
    return [name for name, t in d["theses"].items()
            if t["signals"] >= t.get("threshold", 999)]


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bump")
    b.add_argument("thesis")
    b.add_argument("--n", type=int, default=1)
    b.add_argument("--source")
    sub.add_parser("status")
    sub.add_parser("crossings")
    a = ap.parse_args(argv[1:])

    if a.cmd == "bump":
        t = bump(a.thesis, a.n, a.source)
        print(f"{a.thesis}: {t['signals']}/{t.get('threshold')} "
              f"{'⚠ CROSSED' if t['signals'] >= t.get('threshold', 999) else ''}")
    elif a.cmd == "status":
        for name, t in load()["theses"].items():
            print(f"{name:24} {t['signals']:>3}/{t.get('threshold')}  last={t.get('last_signal')}")
    elif a.cmd == "crossings":
        for name in crossings():
            print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
