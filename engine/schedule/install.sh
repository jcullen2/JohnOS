#!/usr/bin/env bash
# Install the OS producer launchd jobs on JC's Mac. Idempotent — re-run after edits.
# (The Daily is a Cowork task, not launchd — see engine/producers/daily.md.)
# Rewrites __OS_ROOT__ to this repo's absolute path and loads each plist.
set -euo pipefail

OS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENTS="$HOME/Library/LaunchAgents"
mkdir -p "$AGENTS"

for src in "$OS_ROOT"/engine/schedule/*.plist; do
  name="$(basename "$src")"
  dst="$AGENTS/$name"
  sed "s|__OS_ROOT__|$OS_ROOT|g" "$src" > "$dst"
  launchctl unload "$dst" 2>/dev/null || true
  launchctl load "$dst"
  echo "loaded $name"
done

echo "done. verify: launchctl list | grep com.jc.os"
