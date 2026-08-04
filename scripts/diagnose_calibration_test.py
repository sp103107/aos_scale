"""Diagnose Guided Calibration Test pass/fail (simulator).

Documents:
- Healthy path (mass on pan through Test) must Pass.
- Empty pan at Test must Fail (the common field error).
- Note: wrong reference mass still "Passes" Test if pan state is unchanged,
  because Test is algebraically self-consistent with the Loaded capture.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from best_buds_weight_station.operator_runtime import OperatorRuntime  # noqa: E402


def run_cal(
    runtime: OperatorRuntime,
    *,
    reference_g: float,
    loaded_weight_g: float,
    test_weight_g: float | None = None,
) -> dict:
    """Run guided cal; optional different weight during Test."""
    if test_weight_g is None:
        test_weight_g = loaded_weight_g
    runtime.start_calibration()
    runtime.simulator_set_weight(0.0)
    time.sleep(0.25)
    zero = runtime.add_calibration_zero_samples(8)
    runtime.simulator_set_weight(loaded_weight_g)
    time.sleep(0.25)
    loaded = runtime.add_calibration_loaded_samples(reference_g, 8)
    proposal = (loaded.get("data") or {}).get("proposal") or {}
    runtime.simulator_set_weight(test_weight_g)
    time.sleep(0.25)
    try:
        test = runtime.test_calibration(8)
        cal_test = (test.get("data") or {}).get("calibration_test") or {}
        test_status = test.get("status")
        message = test.get("message")
    except RuntimeError as exc:
        # Empty/wrong pan at Test is blocked before the tolerance math runs.
        cal_test = {
            "passed_local_tolerance": False,
            "operator_summary": str(exc),
            "blocked_before_test": True,
        }
        test_status = "blocked"
        message = str(exc)
    return {
        "reference_g": reference_g,
        "loaded_weight_g": loaded_weight_g,
        "test_weight_g": test_weight_g,
        "proposal_factor": proposal.get("proposed_factor"),
        "proposal_predicted_g": proposal.get("predicted_weight_g"),
        "test": cal_test,
        "zero_status": zero.get("status"),
        "loaded_status": loaded.get("status"),
        "test_status": test_status,
        "message": message,
    }


def main() -> int:
    out: dict = {"cases": []}
    with tempfile.TemporaryDirectory(prefix="bbws_cal_diag_") as tmp:
        runtime = OperatorRuntime(data_root=tmp)
        runtime.connect_simulator()
        time.sleep(0.3)

        # Healthy: reference matches mass; mass stays for Test
        ok = run_cal(runtime, reference_g=2000.0, loaded_weight_g=2000.0)
        out["cases"].append({"name": "healthy_2000g", **ok})

        # Field fail: mass removed before Test
        empty_test = run_cal(
            runtime,
            reference_g=2000.0,
            loaded_weight_g=2000.0,
            test_weight_g=0.0,
        )
        out["cases"].append({"name": "empty_pan_at_test", **empty_test})

        # Wrong mass during Loaded+Test still passes Test (self-consistent factor)
        bad_mass = run_cal(runtime, reference_g=2000.0, loaded_weight_g=100.0)
        out["cases"].append({"name": "wrong_mass_self_consistent_pass", **bad_mass})

        runtime.close()

    for case in out["cases"]:
        test = case.get("test") or {}
        case["passed"] = bool(test.get("passed_local_tolerance"))
        case["summary"] = test.get("operator_summary") or case.get("message")

    out["verdict"] = {
        "healthy_should_pass": out["cases"][0]["passed"],
        "empty_pan_at_test_should_fail": not out["cases"][1]["passed"],
        "wrong_mass_self_consistent_passes_test": out["cases"][2]["passed"],
        "gate": "Test requires measured grams within max(1g, 1% of reference)",
        "likely_operator_causes": [
            "Mass removed or shifted between Loaded and Test (most common)",
            "Clicked Test before the pan settled after placing the mass",
            "Reference grams do not match the physical verification mass (factor wrong; Test may still pass)",
        ],
    }
    print(json.dumps(out, indent=2, default=str))
    gate_ok = out["verdict"]["healthy_should_pass"] and out["verdict"]["empty_pan_at_test_should_fail"]
    return 0 if gate_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
