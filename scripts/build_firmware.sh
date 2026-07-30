#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if ! command -v arduino-cli >/dev/null 2>&1; then echo 'arduino-cli unavailable' >&2; exit 3; fi
arduino-cli compile --fqbn arduino:avr:uno "$ROOT/firmware/elegoo_uno_r3_hx711"
