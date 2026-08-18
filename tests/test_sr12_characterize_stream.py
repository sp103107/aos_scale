"""SR12 post-cal characterize stream — ensure worker before 100 g sample collect.

Covers:
- collect_weight_samples restarts a stopped SimulatedFirmwareTransport worker
- characterize_stability can collect after an Accept-style worker stop
- starve errors include last_worker_error when the reader is dead
"""
from __future__ import annotations

import time

import pytest

from best_buds_weight_station.alice.authority import operator_safe_error
from best_buds_weight_station.operator_runtime import OperatorRuntime


def test_collect_weight_samples_ensures_stopped_simulator_worker(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    try:
        result = runtime.connect_simulator()
        assert result["status"] == "completed"
        assert runtime.worker.running
        runtime.worker.stop(stop_stream=True)
        assert not runtime.worker.running
        runtime.last_worker_error = "stale-before-characterize"
        samples = runtime.collect_weight_samples(sample_count=12, timeout_s=5.0, settle_s=0.1)
        assert len(samples) >= 12
        assert runtime.worker.running
        assert runtime.last_worker_error is None
    finally:
        runtime.close()


def test_characterize_stability_after_accept_style_stop(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    try:
        assert runtime.connect_simulator()["status"] == "completed"
        runtime.simulator_set_weight(100.0)
        runtime.worker.stop(stop_stream=True)
        runtime.buffer.clear()
        result = runtime.characterize_stability(sample_count=12, reference_weight_g=100.0)
        assert result["status"] == "completed"
        data = result.get("data") or {}
        characterization = data.get("characterization") or {}
        assert int(characterization.get("sample_count") or 0) >= 12
        assert runtime.worker.running
    finally:
        runtime.close()


def test_collect_weight_samples_attaches_worker_error_when_disconnected(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    try:
        runtime.last_worker_error = "ScaleReadingWorker died"
        with pytest.raises(RuntimeError, match="not enough live weight samples") as exc:
            runtime.collect_weight_samples(sample_count=12, timeout_s=0.2, settle_s=0.0)
        assert "ScaleReadingWorker died" in str(exc.value)
        message = operator_safe_error(exc.value)
        assert "100 g stability test" in message
        assert "Disconnect" in message
    finally:
        runtime.close()


def test_alice_maps_characterize_starve_copy():
    raw = "not enough live weight samples for characterization — place the 100 g mass"
    text = operator_safe_error(RuntimeError(raw))
    assert "live readings" in text
    assert "certif" not in text.lower()
    assert "metrc" not in text.lower()
