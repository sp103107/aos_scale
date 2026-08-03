#!/usr/bin/env bash
# BBWS SR2 S09 — Linux/Xvfb Tk smoke (secondary platform).
# Not a Debian production guarantee. Not a Windows packaging seal.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/app${PYTHONPATH:+:$PYTHONPATH}"

STATUS="fail"
DETAIL="not_run"

if command -v xvfb-run >/dev/null 2>&1; then
  if xvfb-run -a python -m best_buds_weight_station --ui tk --simulator --smoke; then
    STATUS="pass"
    DETAIL="xvfb_tk_simulator_smoke"
  else
    DETAIL="xvfb_tk_smoke_failed"
  fi
elif [[ "$(uname -s)" == "Linux" ]]; then
  DETAIL="xvfb_missing_on_linux"
else
  STATUS="skipped_non_linux_host"
  DETAIL="script_present_host_is_$(uname -s | tr ' ' '_')"
fi

STATUS="$STATUS" DETAIL="$DETAIL" ROOT="$ROOT" python - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
root = Path(os.environ["ROOT"])
receipt = {
    "receipt_type": "bbws_sr2_xvfb_tk_smoke",
    "status": os.environ["STATUS"],
    "detail": os.environ["DETAIL"],
    "compiled_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "non_claims": [
        "Linux smoke ≠ Debian production guarantee",
        "Tk parity ≠ Windows packaging seal",
    ],
}
path = root / "reports" / "bbws_sr2_s09_linux_smoke_receipt.v0.1.0.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(path)
print(json.dumps(receipt, indent=2))
PY

if [[ "${STATUS}" == "fail" ]]; then
  exit 1
fi
exit 0
