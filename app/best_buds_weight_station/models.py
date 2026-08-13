from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
import uuid


def now_rfc3339() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')


def qgram(value: float | Decimal) -> float:
    return float(Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class StabilityProfile:
    profile_id: str = 'standard_hanging_grams'
    window_size: int = 8
    minimum_samples: int = 6
    max_spread_g: float = 0.8
    max_stddev_g: float = 0.25
    settle_ms: int = 650
    minimum_weight_g: float = 1.0
    maximum_weight_g: float = 50000.0
    timeout_ms: int = 15000
    max_trend_g: float = 1.0
    recoverable_timeout: bool = True


@dataclass
class RunContext:
    session_id: str
    run_id: str
    operator_id: str
    facility_id: str
    station_id: str
    cultivar_id: str
    cultivar_raw_name: str
    cultivar_normalized_name: str
    container_id: str
    tare_g: float
    device_id: str = 'SIM-UNO-001'
    firmware_version: str = '0.1.0-sim'
    calibration_id: str = 'SIM-CAL-001'
    stability_profile_id: str = 'standard_hanging_grams'
    evidence_truth_class: str = 'simulator'
    measurement_stage: str = 'harvest'
    weight_purpose: str = 'wet_weight'


@dataclass
class CaptureCommand:
    barcode_raw: str
    gross_g: float
    sample_count: int
    stability_metrics: dict[str, Any]
    capture_mode: str
    raw_adc_value: int | None = None
    duplicate_status: str = 'none'
    operator_note: str | None = None
    void_status: str = 'none'
    source: str = 'serial_simulator'
    idempotency_key: str | None = None


@dataclass
class CommitReceipt:
    receipt_id: str
    record_id: str
    committed_at: str
    authoritative_paths: list[str]
    record_hash: str
    jsonl_event_id: str
    individual_record_path: str
    checkpoint_version: int
    local_commit: bool = True
    status: str = 'committed'
    net_g: float | None = None
    derivative_status: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def create(record_id: str, paths: list[str], record_hash: str, derivatives: dict[str,str], *,
               jsonl_event_id: str, individual_record_path: str, checkpoint_version: int,
               net_g: float | None = None) -> 'CommitReceipt':
        return CommitReceipt(
            str(uuid.uuid4()), record_id, now_rfc3339(), paths, record_hash,
            jsonl_event_id, individual_record_path, checkpoint_version, True,
            'committed', net_g, derivatives,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
