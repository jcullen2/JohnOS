#!/usr/bin/env python3
"""Resolve a queue item: set its status, append the resolution, and move it to
/archive (FOUNDING_SPEC §6). Resolutions are training data for the Friday retro.

    python3 engine/resolve.py queue/<item>.md "approved; sent verbatim"
    python3 engine/resolve.py queue/<item>.md "no longer relevant" --status expired
"""
import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("item", type=Path)
    ap.add_argument("resolution")
    ap.add_argument("--status", default="resolved", choices=["resolved", "expired"])
    ap.add_argument("--ruling", help="JC's ruling verb (DO-IT/APPROVE/SKIP/MORE/…) "
                    "— appended to state/rulings.jsonl for the retro (living loop)")
    a = ap.parse_args(argv[1:])

    if not a.item.exists():
        print(f"no such item: {a.item}")
        return 1
    text = a.item.read_text(encoding="utf-8")
    text = _set_status(text, a.status)
    text += f"\n## Resolution ({date.today().isoformat()}, {a.status})\n{a.resolution}\n"

    ARCHIVE.mkdir(exist_ok=True)
    dst = ARCHIVE / a.item.name
    dst.write_text(text, encoding="utf-8")
    a.item.unlink()

    if a.ruling:
        _log_ruling(a.item.name, a.ruling, a.resolution)
    print(f"resolved → {dst.relative_to(ROOT)}")
    return 0


def _log_ruling(item_name, verb, note):
    """Append a ruling record to state/rulings.jsonl (retro training data)."""
    import json
    rec = {"date": date.today().isoformat(), "item": item_name,
           "ruling": verb, "note": note}
    with (ROOT / "state" / "rulings.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _set_status(text, status):
    out = []
    for line in text.splitlines():
        if line.startswith("status:"):
            line = f"status: {status}"
        out.append(line)
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
