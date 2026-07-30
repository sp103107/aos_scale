#!/bin/sh
set -eu
[ "$#" -ge 1 ] || { echo "Usage: $0 RUN_ID" >&2; exit 2; }
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); cd "$ROOT"
exec "${PYTHON:-python3}" scripts/launcher.py stage resume --run-id "$1" --plan cursor_ready
