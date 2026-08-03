"""Smoke: display-unit conversion + settings action; storage stays grams."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from best_buds_weight_station.operator_runtime import OperatorRuntime  # noqa: E402
from best_buds_weight_station.units import display_to_grams, format_weight, grams_to_display  # noqa: E402


def main() -> int:
    assert abs(display_to_grams(1.0, "kg") - 1000.0) < 1e-9
    assert abs(display_to_grams(1.0, "lb") - 453.59237) < 1e-9
    assert abs(grams_to_display(1000.0, "kg") - 1.0) < 1e-9
    assert "lb" in format_weight(453.59237, "lb")
    with tempfile.TemporaryDirectory(prefix="bbws_sr2_unit_") as tmp:
        runtime = OperatorRuntime(data_root=tmp)
        result = runtime.dispatch("settings.display_unit.set", {"display_unit": "kg"})
        assert result["status"] == "completed", result
        snap = runtime.snapshot()
        assert snap["display_unit"] == "kg"
        assert snap["storage_unit"] == "g"
        runtime.close()
    print(json.dumps({"status": "PASS", "display_unit": "kg", "storage_unit": "g"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
