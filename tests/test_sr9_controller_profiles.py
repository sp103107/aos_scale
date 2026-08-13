"""
SR9 controller/runtime wiring for scale profiles and characterization.

Covers characterize recommendation, confirm → active profile, archive-of-active
rejection, and set_device_id on the firmware simulator. Not legal-for-trade.
"""
from __future__ import annotations

import pytest

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.application_controller import ApplicationController
from best_buds_weight_station.operator_runtime import OperatorRuntime


def _quiet_samples(center: float = 100.0, count: int = 24) -> list[float]:
    # Mild oscillation so metrics stay finite and near the 100 g reference.
    out: list[float] = []
    for i in range(count):
        out.append(center + (0.15 if i % 2 == 0 else -0.15))
    return out


def test_characterize_returns_recommendation(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.connect_simulator()
    runtime.set_device_id("BBWS-SCALE-001")
    result = runtime.characterize_stability(
        _quiet_samples(),
        reference_weight_g=100.0,
    )
    assert result["status"] == "completed"
    data = result["data"]
    assert data.get("auto_activated") is False
    recommended = data.get("recommended_stability") or {}
    assert recommended.get("max_spread_g") is not None
    assert recommended.get("max_stddev_g") is not None
    assert recommended.get("window_size") == 16
    characterization = data.get("characterization") or {}
    assert characterization.get("characterization_receipt_id")
    runtime.close()


def test_confirm_creates_active_profile(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.connect_simulator()
    runtime.set_device_id("BBWS-SCALE-002")
    char = runtime.characterize_stability(_quiet_samples(), reference_weight_g=100.0)
    recommended = char["data"]["recommended_stability"]
    receipt_id = char["data"]["characterization"]["characterization_receipt_id"]
    confirmed = runtime.confirm_stability_profile(
        device_id="BBWS-SCALE-002",
        stability=recommended,
        name="Hanging 002",
        characterization_receipt_id=receipt_id,
    )
    assert confirmed["status"] == "completed"
    profile = confirmed["data"]["profile"]
    assert profile["status"] == "active"
    assert profile["device_id"] == "BBWS-SCALE-002"
    assert profile["name"] == "Hanging 002"
    assert profile["stability"]["max_spread_g"] == recommended["max_spread_g"]
    active = runtime.controller.scale_profiles.get_active_for_device("BBWS-SCALE-002")
    assert active is not None
    assert active.profile_id == profile["profile_id"]
    runtime.close()


def test_archive_active_fails_via_action(tmp_path):
    controller = ApplicationController(tmp_path / "cfg")
    created = controller.scale_profiles.create(
        name="Active A",
        device_id="BBWS-SCALE-003",
        calibration_factor=42.0,
        activate=True,
    )
    result = controller.dispatch(
        ActionRequest("scale.profile.archive", {"profile_id": created.profile_id})
    )
    assert result.status == "failed"
    assert "active" in (result.message or "").lower() or "active" in str(
        (result.data or {}).get("error_detail", "")
    ).lower()


def test_set_device_id_on_simulator(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.connect_simulator()
    result = runtime.set_device_id("BBWS-SCALE-010")
    assert result["status"] == "completed"
    assert result["data"]["device_id"] == "BBWS-SCALE-010"
    assert runtime.controller.device is not None
    assert runtime.controller.device.status.device_id == "BBWS-SCALE-010"
    status = runtime.dispatch("device.status")
    assert status["data"]["device_status"]["device_id"] == "BBWS-SCALE-010"
    runtime.close()
