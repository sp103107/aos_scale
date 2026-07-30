#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); cd "$ROOT"
exec "${PYTHON:-python3}" scripts/launcher.py stage run-plan --plan cursor_ready --run-id cursor-ready-v0.1.7 "$@"
