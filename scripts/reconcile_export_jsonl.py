"""
CLI: reconcile session export derivatives against authoritative JSONL.

Usage:
  python scripts/reconcile_export_jsonl.py <session_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from best_buds_weight_station.reports import reconcile_export_to_jsonl  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python scripts/reconcile_export_jsonl.py <session_dir>", file=sys.stderr)
        return 2
    session_dir = Path(argv[1]).expanduser().resolve()
    receipt = reconcile_export_to_jsonl(session_dir)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
