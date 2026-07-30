#!/bin/sh
set -eu
[ "$#" -ge 1 ] || { echo "Usage: $0 STAGE_ID" >&2; exit 2; }
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); cd "$ROOT"
exec "${PYTHON:-python3}" scripts/launcher.py stage run --stage "$1" --run-id manual-stage
