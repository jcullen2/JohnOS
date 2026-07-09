#!/usr/bin/env python3
"""Lint queue files against the schema (engine/schema.md).

Usage:
    python3 engine/validate.py [path ...]      # defaults to queue/*.md
Exit code 1 if any file has errors (warnings never fail the lint).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qitem import load, validate  # noqa: E402  (sibling module)

ROOT = Path(__file__).resolve().parent.parent


def main(argv):
    paths = [Path(a) for a in argv[1:]] or sorted((ROOT / "queue").glob("*.md"))
    if not paths:
        print("no queue files found")
        return 0

    n_err = n_warn = 0
    for p in paths:
        try:
            errs, warns = validate(load(p))
        except Exception as e:  # unreadable / malformed file
            errs, warns = [f"could not parse: {e}"], []
        rel = p.relative_to(ROOT) if ROOT in p.resolve().parents else p
        for e in errs:
            print(f"ERROR  {rel}: {e}")
        for w in warns:
            print(f"warn   {rel}: {w}")
        n_err += len(errs)
        n_warn += len(warns)

    print(f"\n{len(paths)} file(s): {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
