#!/bin/sh
# Prefer python3, then python. Runtime still fail-opens if neither exists (ADR 007).
DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$DIR/fence.py"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$DIR/fence.py"
fi
echo "fence: neither python3 nor python on PATH; allowing (fail-open)" >&2
printf '%s\n' '{"permission":"allow"}'
exit 0
