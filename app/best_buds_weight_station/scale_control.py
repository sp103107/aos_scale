from __future__ import annotations

import json
import math
import statistics
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .device_service import DeviceProtocolError, DeviceService
from .models import now_rfc3339, qgram
from .storage import atomic_json, safe_component


@dataclass
class ZeroReceipt:
    receipt_id: str
    device_id: str | None
    status: str
    sample_count: int
    mean_g: float
    spread_g: float
    tolerance_g: float
    created_at: str = field(default_factory=now_rfc3339)
    truth_class: str = "UNIT_TEST_PASS"
    physical_device_pass: bool = False


@dataclass
class TareRecord:
    tare_id: str
    container_id: str
    tare_g: float
    source: str
    operator_id: str
    created_at: str = field(default_factory=now_rfc3339)
    truth_class: str = "UNIT_TEST_PASS"


@dataclass
class CalibrationProposal:
    calibration_session_id: str
    reference_weight_g: float
    zero_raw_mean: float
    loaded_raw_mean: float
    raw_spread: float
    proposed_factor: float
    predicted_weight_g: float
    error_g: float
    relative_error_percent: float
    accepted: bool = False
    created_at: str = field(default_factory=now_rfc3339)


class ScaleControlService:
    def __init__(self, device: DeviceService, session_dir: str | Path):
        self.device = device
        self.session_dir = Path(session_dir).resolve()
        self.tare_dir = self.session_dir / "tare_records"
        self.calibration_dir = self.session_dir / "calibration_receipts"
        self.zero_dir = self.session_dir / "zero_receipts"
        self.active_calibration: dict[str, Any] | None = None

    @staticmethod
    def _metrics(values: Iterable[float]) -> tuple[float, float, float]:
        samples = [float(value) for value in values]
        if len(samples) < 3:
            raise ValueError("at least three samples are required")
        if any(not math.isfinite(value) for value in samples):
            raise ValueError("samples must be finite")
        mean = statistics.fmean(samples)
        spread = max(samples) - min(samples)
        stddev = statistics.pstdev(samples)
        return mean, spread, stddev

    @classmethod
    def _robust_center(cls, values: Iterable[float]) -> tuple[float, float, float]:
        """Trim one high/low sample before mean/spread (calibration captures)."""
        samples = [float(value) for value in values]
        if len(samples) >= 5:
            samples = sorted(samples)[1:-1]
        return cls._metrics(samples)

    def zero_scale(
        self,
        readings_g: Iterable[float] | None = None,
        *,
        tolerance_g: float = 0.8,
        sample_count: int = 8,
    ) -> ZeroReceipt:
        # Clear any previous host zero, attempt firmware TARE, then establish a
        # host display zero. With calibration_factor still ~1.0, firmware grams are
        # essentially raw counts; host zero is what makes the UI leave -380000.
        #
        # Important: the main UI shows median host-zeroed weight (calm 1–2 g crawl).
        # ZERO samples the device directly after clearing that offset, so spread can
        # look like 100–300 "g" of ADC noise even when the pan is still.
        previous_offset = float(self.device.host_zero_offset_g)
        previous_invert = bool(self.device.invert_weight_sign)
        self.device.clear_host_zero()
        tare_ok = True
        try:
            self.device.tare()
        except DeviceProtocolError:
            tare_ok = False
        # Settle after firmware TARE so DOUT/stream are not mid-conversion.
        self.device.sleep(0.45)
        values = [float(value) for value in readings_g] if readings_g is not None else []
        if not values:
            # Discard a couple of post-TARE conversions, then collect.
            for _ in range(2):
                try:
                    self.device.read_weight()
                except Exception:
                    break
            values = [float(self.device.read_weight()["weight_g"]) for _ in range(max(5, sample_count))]
        mean, spread, _ = self._metrics(values)
        # Trim one high/low sample so a single glitch does not fail a still pan.
        check_spread = spread
        if len(values) >= 5:
            ordered = sorted(values)
            trimmed = ordered[1:-1]
            check_spread = max(trimmed) - min(trimmed)
        # Invert only for large negative baselines (uncalibrated raw counts). After a
        # good SET_CAL, empty-pan residuals are small — do not flip polarity on noise.
        cal = self.device.status.calibration_factor
        calibrated = cal is not None and abs(float(cal) - 1.0) >= 1e-6
        invert = mean < -1.0 and abs(mean) >= 100.0
        if invert:
            values = [-value for value in values]
            mean = -mean
            if len(values) >= 5:
                ordered = sorted(values)
                trimmed = ordered[1:-1]
                check_spread = max(trimmed) - min(trimmed)
            else:
                _, check_spread, _ = self._metrics(values)
        # Tolerance bands:
        # - uncalibrated: firmware "g" ≈ ADC counts; allow typical count noise
        # - large residual: relative band
        # - calibrated near-zero: a few real grams of hang noise
        peak = max(abs(mean), abs(statistics.median(values)), 1.0)
        if not calibrated:
            effective_tol = max(float(tolerance_g), 350.0, (0.01 * peak) + 50.0)
        elif abs(mean) > 500.0:
            effective_tol = max(float(tolerance_g), (0.002 * abs(mean)) + 5.0)
        elif abs(mean) < 50.0:
            effective_tol = max(float(tolerance_g), 3.0)
        else:
            effective_tol = max(float(tolerance_g), 5.0)
        self.device.set_host_zero_offset(mean, invert_sign=invert)
        status = "zeroed" if check_spread <= effective_tol else "failed"
        receipt = ZeroReceipt(
            receipt_id=f"zero-{uuid.uuid4()}",
            device_id=self.device.status.device_id,
            status=status,
            sample_count=len(values),
            mean_g=qgram(0.0 if status == "zeroed" else mean),
            spread_g=qgram(check_spread),
            tolerance_g=qgram(effective_tol),
            truth_class="SIMULATOR_PASS" if self.device.mode.value == "serial_simulator" else "UNIT_TEST_PASS",
        )
        atomic_json(
            self.zero_dir / f"{receipt.receipt_id}.json",
            {
                **asdict(receipt),
                "firmware_tare_ok": tare_ok,
                "host_zero_offset_g": self.device.host_zero_offset_g,
                "invert_weight_sign": self.device.invert_weight_sign,
                "baseline_mean_g": qgram(mean),
                "calibrated_path": calibrated,
                "raw_spread_g": qgram(spread),
            },
        )
        if status != "zeroed":
            # Keep the previous display zero so a failed ZERO does not make the UI jump wild.
            self.device.set_host_zero_offset(previous_offset, invert_sign=previous_invert)
            hint = (
                ""
                if calibrated
                else " Scale looks uncalibrated — finish Guided Calibration if live numbers are huge/wild."
            )
            raise ValueError(
                f"zero stability validation failed: empty-pan samples swung ~{qgram(check_spread)} "
                f"(limit {qgram(effective_tol)}). "
                "The main live number is averaged and can look calm while ZERO samples the device directly. "
                "Leave the pan empty, wait 2 seconds, press ZERO again."
                f"{hint}"
            )
        return receipt

    def set_known_tare(self, container_id: str, tare_g: float, operator_id: str) -> TareRecord:
        safe_component(container_id, "container_id")
        safe_component(operator_id, "operator_id")
        value = qgram(tare_g)
        if value < 0 or value > 10000:
            raise ValueError("tare is outside supported bounds")
        record = TareRecord(
            tare_id=f"tare-{uuid.uuid4()}",
            container_id=container_id,
            tare_g=value,
            source="operator_entered",
            operator_id=operator_id,
        )
        atomic_json(self.tare_dir / f"{container_id}.json", asdict(record))
        return record

    def capture_tare(self, container_id: str, readings_g: Iterable[float], operator_id: str,
                     *, max_spread_g: float = 0.8) -> TareRecord:
        values = list(readings_g)
        mean, spread, _ = self._metrics(values)
        # Allow inverted-polarity empty-pan readings during bring-up; store magnitude for net math.
        if spread > max_spread_g:
            raise ValueError("container tare reading is not stable")
        tare_value = abs(mean)
        if tare_value > 10000:
            raise ValueError("tare is outside supported bounds")
        record = self.set_known_tare(container_id, tare_value, operator_id)
        record.source = "captured_stable_weight"
        record.truth_class = "SIMULATOR_PASS" if self.device.mode.value == "serial_simulator" else "UNIT_TEST_PASS"
        atomic_json(self.tare_dir / f"{container_id}.json", asdict(record))
        return record

    def load_tare(self, container_id: str) -> TareRecord:
        safe_component(container_id, "container_id")
        data = json.load((self.tare_dir / f"{container_id}.json").open(encoding="utf-8"))
        return TareRecord(**data)

    def start_calibration(self, *, active_capture: bool, operator_id: str, maintenance_authorized: bool) -> str:
        if active_capture:
            raise RuntimeError("calibration is blocked during active capture")
        if not maintenance_authorized:
            raise PermissionError("maintenance authorization is required")
        safe_component(operator_id, "operator_id")
        session_id = f"cal-{uuid.uuid4()}"
        self.active_calibration = {
            "calibration_session_id": session_id,
            "operator_id": operator_id,
            "zero_raw_samples": [],
            "loaded_raw_samples": [],
            "reference_weight_g": None,
            "stage": "zero_samples",
            "created_at": now_rfc3339(),
        }
        return session_id

    def add_calibration_samples(self, kind: str, samples: Iterable[float], *, reference_weight_g: float | None = None) -> None:
        if not self.active_calibration:
            raise RuntimeError("calibration is not active")
        values = [float(value) for value in samples]
        if len(values) < 3 or any(not math.isfinite(value) for value in values):
            raise ValueError("valid calibration samples are required")
        if kind == "zero":
            # Replace (do not accumulate) so a re-click is not mixed with a bad first take.
            self.active_calibration["zero_raw_samples"] = values
            self.active_calibration["stage"] = "loaded_samples"
        elif kind == "loaded":
            if reference_weight_g is None or reference_weight_g <= 0:
                raise ValueError("verified reference weight is required")
            self.active_calibration["reference_weight_g"] = float(reference_weight_g)
            self.active_calibration["loaded_raw_samples"] = values
            self.active_calibration["stage"] = "proposal_ready"
        else:
            raise ValueError("sample kind must be zero or loaded")

    def calculate_calibration(self) -> CalibrationProposal:
        if not self.active_calibration or self.active_calibration.get("stage") != "proposal_ready":
            raise RuntimeError("calibration samples are incomplete")
        zero_mean, zero_spread, _ = self._robust_center(self.active_calibration["zero_raw_samples"])
        loaded_mean, loaded_spread, _ = self._robust_center(self.active_calibration["loaded_raw_samples"])
        delta = loaded_mean - zero_mean
        if abs(delta) < 1e-9:
            raise ValueError("raw calibration delta is zero")
        reference = float(self.active_calibration["reference_weight_g"])
        factor = delta / reference
        predicted = delta / factor
        error = predicted - reference
        proposal = CalibrationProposal(
            calibration_session_id=self.active_calibration["calibration_session_id"],
            reference_weight_g=qgram(reference),
            zero_raw_mean=zero_mean,
            loaded_raw_mean=loaded_mean,
            raw_spread=max(zero_spread, loaded_spread),
            proposed_factor=factor,
            predicted_weight_g=qgram(predicted),
            error_g=qgram(error),
            relative_error_percent=round(abs(error) / reference * 100.0, 6),
        )
        self.active_calibration["proposal"] = asdict(proposal)
        self.active_calibration["stage"] = "test_ready"
        return proposal

    @staticmethod
    def calibration_test_tolerance_g(reference_weight_g: float) -> float:
        """Local Test pass band (not legal-for-trade).

        Light references need a wider absolute band; 1% of 100 g is only 1 g and
        is tighter than typical hanging HX711 noise at that load.
        """
        reference = float(reference_weight_g)
        if reference <= 250.0:
            return max(5.0, reference * 0.05)
        return max(2.0, reference * 0.01)

    def test_calibration(self, raw_samples: Iterable[float]) -> dict[str, Any]:
        if not self.active_calibration or "proposal" not in self.active_calibration:
            raise RuntimeError("calibration proposal is unavailable")
        proposal = self.active_calibration["proposal"]
        mean, spread, stddev = self._robust_center(raw_samples)
        zero_raw = float(proposal["zero_raw_mean"])
        loaded_raw = float(proposal["loaded_raw_mean"])
        factor = float(proposal["proposed_factor"])
        weight = (mean - zero_raw) / factor
        reference = float(proposal["reference_weight_g"])
        # Light references need a wider gram band — HX711 hang noise at 100 g can be
        # several grams, and 1% of 100 g (=1 g) is tighter than the hardware can hold.
        tol = self.calibration_test_tolerance_g(reference)
        passed = abs(weight - reference) <= tol
        # How far Test raw drifted from the Loaded capture (same pan should stay close).
        loaded_delta = loaded_raw - zero_raw
        test_delta = mean - zero_raw
        pan_ratio = abs(test_delta / loaded_delta) if abs(loaded_delta) > 1e-9 else 0.0
        if passed:
            summary = (
                f"Measured ~{qgram(weight)} g vs reference {reference} g "
                f"(need within {qgram(tol)} g). Pass — you can Accept."
            )
        elif pan_ratio <= 0.15 or abs(weight) <= max(1.0, 0.05 * reference):
            # Near-empty / mass removed between Loaded and Test — most common fail.
            summary = (
                f"Measured ~{qgram(weight)} g vs reference {reference} g "
                f"(need within {qgram(tol)} g). Fail — the reference mass does not appear to be on the pan "
                "(Test readings look empty compared with Loaded). "
                "Put the SAME verified mass back on, wait for settle, then run Test again. "
                "Calibration was not saved."
            )
        elif 1.3 <= pan_ratio <= 3.0:
            # Classic mid-settle Loaded + full-settle Test (e.g. 193 g vs 100 g reference).
            summary = (
                f"Measured ~{qgram(weight)} g vs reference {reference} g "
                f"(need within {qgram(tol)} g). Fail — Loaded was probably captured while the pan "
                "was still climbing. Start over: empty → Zero samples → place mass → wait until the "
                "live number stops moving → Loaded samples → leave mass on → Test. "
                "Calibration was not saved."
            )
        elif 0.7 <= pan_ratio < 1.0:
            summary = (
                f"Measured ~{qgram(weight)} g vs reference {reference} g "
                f"(need within {qgram(tol)} g). Fail — Test reads lighter than Loaded "
                "(mass may have shifted, or Loaded caught a high bounce). "
                "Seat the mass firmly, wait until the live number stops moving, recapture Loaded, "
                "then Test again. A heavier reference (500 g–2 kg) is more reliable. "
                "Calibration was not saved."
            )
        else:
            summary = (
                f"Measured ~{qgram(weight)} g vs reference {reference} g "
                f"(need within {qgram(tol)} g). Fail — large difference. "
                "Leave the same mass on from Loaded through Test, enter reference in grams, "
                "wait for settle, run Test again. Calibration was not saved."
            )
        result = {
            "test_weight_g": qgram(weight),
            "reference_weight_g": reference,
            "error_g": qgram(weight - reference),
            "relative_error_percent": round(abs(weight - reference) / reference * 100.0, 6),
            "tolerance_g": qgram(tol),
            "raw_spread": spread,
            "raw_stddev": stddev,
            "passed_local_tolerance": passed,
            "truth_class": "SIMULATOR_PASS" if self.device.mode.value == "serial_simulator" else "UNIT_TEST_PASS",
            "non_claim": "This is not legal-for-trade certification.",
            "operator_summary": summary,
        }
        self.active_calibration["test_result"] = result
        # Only advance to Accept when the local check passed (avoids dead-end Accept clicks).
        self.active_calibration["stage"] = "acceptance_ready" if passed else "test_ready"
        return result

    def accept_calibration(self, *, maintenance_authorized: bool, second_confirmation: bool) -> dict[str, Any]:
        if not self.active_calibration or self.active_calibration.get("stage") != "acceptance_ready":
            test = (self.active_calibration or {}).get("test_result") or {}
            if test and not test.get("passed_local_tolerance"):
                raise ValueError(
                    test.get("operator_summary")
                    or (
                        "Calibration test did not match closely enough. Keep the same mass on the pan, "
                        "wait for settle, run Test again. Calibration was not saved."
                    )
                )
            raise RuntimeError("Run Test successfully before Accept. Calibration is not ready yet.")
        if not maintenance_authorized or not second_confirmation:
            raise PermissionError("maintenance authorization and second confirmation are required")
        test = self.active_calibration["test_result"]
        if not test["passed_local_tolerance"]:
            raise ValueError(
                test.get("operator_summary")
                or "Calibration test did not pass local tolerance. Calibration was not saved."
            )
        proposal = self.active_calibration["proposal"]
        self.device.set_calibration(float(proposal["proposed_factor"]))
        status = self.device.read_status()
        accepted_factor = float(status["calibration_factor"])
        if not math.isclose(accepted_factor, float(proposal["proposed_factor"]), rel_tol=1e-5, abs_tol=1e-5):
            raise RuntimeError("device did not report the accepted calibration factor")
        receipt = {
            "receipt_id": f"calibration-{uuid.uuid4()}",
            "calibration_session_id": proposal["calibration_session_id"],
            "status": "accepted",
            "accepted_factor": accepted_factor,
            "device_id": self.device.status.device_id,
            "operator_id": self.active_calibration["operator_id"],
            "proposal": proposal,
            "test_result": test,
            "created_at": now_rfc3339(),
            "truth_class": "SIMULATOR_PASS" if self.device.mode.value == "serial_simulator" else "UNIT_TEST_PASS",
            "physical_device_pass": False,
            "non_claims": [
                "No legal-for-trade certification is claimed.",
                "No physical calibration pass is claimed without physical evidence.",
            ],
        }
        atomic_json(self.calibration_dir / f"{receipt['receipt_id']}.json", receipt)
        self.active_calibration = None
        return receipt

    def cancel_calibration(self) -> dict[str, Any]:
        prior = self.active_calibration
        self.active_calibration = None
        return {"status": "cancelled", "had_active_session": prior is not None, "created_at": now_rfc3339()}
