from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from .models import CaptureCommand, CommitReceipt, RunContext, now_rfc3339, qgram
from .spreadsheet import append_csv, append_xlsx


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def safe_component(value: str, label: str) -> str:
    text = str(value).strip()
    if not text or text in {".", ".."} or "/" in text or "\\" in text or "\x00" in text:
        raise ValueError(f"invalid {label}")
    return text


def fsync_directory(path: Path) -> bool:
    """Best-effort directory synchronization after atomic rename.

    Returns False on platforms/filesystems that do not support directory fsync.
    The caller records this boundary rather than claiming stronger durability.
    """
    try:
        fd = os.open(str(path), os.O_RDONLY)
    except (OSError, AttributeError):
        return False
    try:
        os.fsync(fd)
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def atomic_json(path: Path, obj: Any, *, fail_during: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    payload = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    if fail_during:
        raise OSError(f"injected atomic replacement interruption for {path.name}")
    os.replace(tmp, path)
    return fsync_directory(path.parent)


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL line {number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"invalid JSONL line {number}: object required")
            rows.append(value)
    return rows


def quarantine_incomplete_jsonl_tail(path: Path, quarantine_dir: Path) -> dict[str, Any]:
    """Quarantine only an invalid final JSONL fragment.

    Earlier-line corruption is never repaired automatically. This function is
    intentionally conservative and only removes a final unterminated/invalid
    fragment produced by an interrupted append.
    """
    if not path.exists() or path.stat().st_size == 0:
        return {"repaired": False, "reason": "empty_or_missing"}
    data = path.read_bytes()
    boundaries = [index + 1 for index, byte in enumerate(data) if byte == 0x0A]
    last_complete = boundaries[-1] if boundaries else 0
    tail = data[last_complete:]
    if not tail.strip():
        return {"repaired": False, "reason": "complete"}
    try:
        decoded = tail.decode("utf-8")
        json.loads(decoded)
        # A valid object without a final newline is normalized, not discarded.
        with path.open("ab") as handle:
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        return {"repaired": True, "reason": "newline_restored", "quarantined": None}
    except Exception:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        target = quarantine_dir / f"records_tail_{uuid.uuid4().hex}.jsonl.partial"
        target.write_bytes(tail)
        with path.open("r+b") as handle:
            handle.truncate(last_complete)
            handle.flush()
            os.fsync(handle.fileno())
        fsync_directory(path.parent)
        return {"repaired": True, "reason": "invalid_tail_quarantined", "quarantined": str(target)}


class DuplicateCommitError(ValueError):
    def __init__(self, idempotency_key: str, record_id: str, receipt_id: str | None):
        super().__init__("duplicate idempotency key")
        self.idempotency_key = idempotency_key
        self.record_id = record_id
        self.receipt_id = receipt_id

    def to_result(self) -> dict[str, Any]:
        return {
            "status": "duplicate",
            "idempotency_key": self.idempotency_key,
            "record_id": self.record_id,
            "original_receipt_id": self.receipt_id,
        }


class CommitStepError(OSError):
    def __init__(self, failure_code: str, message: str, *, jsonl_event_id: str | None = None):
        super().__init__(message)
        self.failure_code = failure_code
        self.jsonl_event_id = jsonl_event_id

    def to_result(self) -> dict[str, Any]:
        return {
            "status": "failure",
            "failure_code": self.failure_code,
            "local_commit": False,
            "jsonl_event_id": self.jsonl_event_id,
        }


class SessionStore:
    def __init__(
        self,
        data_root: str | Path,
        context: RunContext,
        fail_step: str | None = None,
        *,
        recent_pointer_path: str | Path | None = None,
    ):
        self.data_root = Path(data_root).expanduser().resolve()
        self.context = context
        session = safe_component(context.session_id, "session_id")
        self.session_dir = self.data_root / "sessions" / session
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.records_path = self.session_dir / "records.jsonl"
        self.records_dir = self.session_dir / "records"
        self.snapshot_path = self.session_dir / "session_snapshot.json"
        self.manifest_path = self.session_dir / "session_manifest.json"
        self.pending_dir = self.session_dir / "pending_sync"
        self.receipts_dir = self.session_dir / "receipts"
        self.recovery_dir = self.session_dir / "recovery_receipts"
        self.quarantine_dir = self.session_dir / "quarantine"
        self.fail_step = fail_step
        self.recent_pointer_path = Path(recent_pointer_path).expanduser().resolve() if recent_pointer_path else None
        self.directory_fsync_supported: bool | None = None
        self._recover_index()

    def _recover_index(self) -> None:
        if not hasattr(self, "startup_tail_repair"):
            self.startup_tail_repair = quarantine_incomplete_jsonl_tail(self.records_path, self.quarantine_dir)
        rows = parse_jsonl(self.records_path)
        self.sequence = 0
        self.previous_hash: str | None = None
        self.barcodes: set[str] = set()
        self.idempotency_map: dict[str, dict[str, str | None]] = {}
        for row in rows:
            if row.get("event_type") != "weight_record":
                continue
            self.sequence = max(self.sequence, int(row["sequence"]))
            self.previous_hash = row["record_hash"]
            self.barcodes.add(row["barcode_normalized"])
            if row.get("idempotency_key"):
                self.idempotency_map[row["idempotency_key"]] = {
                    "record_id": row["record_id"],
                    "receipt_id": None,
                }
        for receipt_path in self.receipts_dir.glob("*.json") if self.receipts_dir.exists() else []:
            try:
                receipt = json.load(receipt_path.open(encoding="utf-8"))
            except Exception:
                continue
            for value in self.idempotency_map.values():
                if value["record_id"] == receipt.get("record_id"):
                    value["receipt_id"] = receipt.get("receipt_id")
        if not self.manifest_path.exists():
            self.directory_fsync_supported = atomic_json(
                self.manifest_path,
                {
                    "schema_version": "1.0.0",
                    "session_id": self.context.session_id,
                    "run_id": self.context.run_id,
                    "created_at": now_rfc3339(),
                    "status": "active",
                    "context": self.context.__dict__,
                },
            )
        self.recovery_required = self._recovery_needed(rows)

    def _recovery_needed(self, rows: list[dict[str, Any]] | None = None) -> bool:
        rows = rows if rows is not None else parse_jsonl(self.records_path)
        weights = [row for row in rows if row.get("event_type") == "weight_record"]
        if getattr(self, "startup_tail_repair", {}).get("repaired"):
            return True
        if any(self.session_dir.rglob("*.tmp")):
            return True
        if not weights:
            return False
        last = weights[-1]
        try:
            snapshot = json.load(self.snapshot_path.open(encoding="utf-8"))
        except Exception:
            return True
        if int(snapshot.get("last_sequence", 0)) < int(last["sequence"]):
            return True
        for row in weights:
            path = self.records_dir / f"{int(row['sequence']):06d}_{row['record_id']}.json"
            if not path.exists():
                return True
        if any(value.get("receipt_id") in (None, "") for value in self.idempotency_map.values()):
            return True
        return False

    def verify_chain(self) -> tuple[bool, str]:
        previous: str | None = None
        for row in parse_jsonl(self.records_path):
            if row.get("event_type") != "weight_record":
                continue
            claimed = row["record_hash"]
            body = dict(row)
            body.pop("record_hash", None)
            if body.get("previous_record_hash") != previous:
                return False, "previous_hash_mismatch"
            if sha(body) != claimed:
                return False, "record_hash_mismatch"
            previous = claimed
        return True, "ok"

    def _append_record(self, record: dict[str, Any]) -> None:
        line = canonical(record) + "\n"
        if self.fail_step in {"before_jsonl", "jsonl"}:
            raise CommitStepError("AUTHORITATIVE_APPEND_FAILED", "injected JSONL failure")
        self.records_path.parent.mkdir(parents=True, exist_ok=True)
        if self.fail_step == "during_jsonl":
            fragment = line[: max(1, len(line) // 2)].encode("utf-8")
            with self.records_path.open("ab") as handle:
                handle.write(fragment)
                handle.flush()
                os.fsync(handle.fileno())
            raise CommitStepError(
                "AUTHORITATIVE_APPEND_INTERRUPTED",
                "injected interruption during JSONL append",
                jsonl_event_id=record["event_id"],
            )
        with self.records_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        if self.fail_step == "after_jsonl":
            raise CommitStepError(
                "POST_APPEND_INTERRUPTED",
                "injected interruption after JSONL append",
                jsonl_event_id=record["event_id"],
            )

    def _write_recent_pointer(self, record: dict[str, Any]) -> None:
        if self.recent_pointer_path is None:
            return
        if self.fail_step == "recent_pointer":
            raise CommitStepError(
                "RECENT_RUN_POINTER_FAILED",
                "injected recent-run pointer failure",
                jsonl_event_id=record["event_id"],
            )
        atomic_json(
            self.recent_pointer_path,
            {
                "schema_version": "1.0.0",
                "session_id": self.context.session_id,
                "run_id": self.context.run_id,
                "session_manifest": str(self.manifest_path),
                "data_root": str(self.data_root),
                "last_sequence": int(record["sequence"]),
                "last_record_id": record["record_id"],
                "updated_at": now_rfc3339(),
            },
        )

    def commit(self, cmd: CaptureCommand) -> tuple[dict[str, Any], CommitReceipt]:
        if cmd.idempotency_key and cmd.idempotency_key in self.idempotency_map:
            original = self.idempotency_map[cmd.idempotency_key]
            raise DuplicateCommitError(cmd.idempotency_key, str(original["record_id"]), original.get("receipt_id"))
        barcode_raw = cmd.barcode_raw.strip()
        if not barcode_raw:
            raise ValueError("barcode required")
        gross = qgram(cmd.gross_g)
        tare = qgram(self.context.tare_g)
        net = qgram(gross - tare)
        if net < 0:
            raise ValueError("net weight cannot be negative")
        duplicate = "warning" if barcode_raw.upper() in self.barcodes and cmd.duplicate_status == "none" else cmd.duplicate_status
        event_id = str(uuid.uuid4())
        record: dict[str, Any] = {
            "event_type": "weight_record",
            "event_id": event_id,
            "record_id": str(uuid.uuid4()),
            "session_id": self.context.session_id,
            "run_id": self.context.run_id,
            "sequence": self.sequence + 1,
            "barcode_raw": barcode_raw,
            "barcode_normalized": barcode_raw.upper(),
            "captured_at": now_rfc3339(),
            "operator_id": self.context.operator_id,
            "facility_id": self.context.facility_id,
            "station_id": self.context.station_id,
            "cultivar_id": self.context.cultivar_id,
            "cultivar_raw_name": self.context.cultivar_raw_name,
            "cultivar_normalized_name": self.context.cultivar_normalized_name,
            "container_id": self.context.container_id,
            "tare_g": tare,
            "gross_g": gross,
            "net_g": net,
            "device_id": self.context.device_id,
            "firmware_version": self.context.firmware_version,
            "calibration_id": self.context.calibration_id,
            "raw_adc_value": cmd.raw_adc_value,
            "sample_count": cmd.sample_count,
            "stability_profile_id": self.context.stability_profile_id,
            "stability_metrics": cmd.stability_metrics,
            "capture_mode": cmd.capture_mode,
            "duplicate_status": duplicate,
            "operator_note": cmd.operator_note,
            "source": cmd.source,
            "record_status": "accepted",
            "previous_record_hash": self.previous_hash,
            "idempotency_key": cmd.idempotency_key,
            "evidence_truth_class": self.context.evidence_truth_class,
        }
        record["record_hash"] = sha(record)

        self._append_record(record)
        individual = self.records_dir / f"{record['sequence']:06d}_{record['record_id']}.json"
        if self.fail_step in {"before_individual", "individual_json"}:
            self._recover_index()
            raise CommitStepError(
                "INDIVIDUAL_RECORD_WRITE_FAILED",
                "injected individual JSON failure",
                jsonl_event_id=event_id,
            )
        try:
            atomic_json(individual, record, fail_during=self.fail_step == "during_individual")
        except OSError as exc:
            self._recover_index()
            raise CommitStepError(
                "INDIVIDUAL_RECORD_WRITE_FAILED",
                str(exc),
                jsonl_event_id=event_id,
            ) from exc
        if self.fail_step == "after_individual":
            self._recover_index()
            raise CommitStepError(
                "POST_INDIVIDUAL_INTERRUPTED",
                "injected interruption after individual JSON",
                jsonl_event_id=event_id,
            )

        snapshot = {
            "schema_version": "1.0.0",
            "session_id": self.context.session_id,
            "run_id": self.context.run_id,
            "checkpoint_version": record["sequence"],
            "last_sequence": record["sequence"],
            "last_record_id": record["record_id"],
            "last_record_hash": record["record_hash"],
            "record_count": record["sequence"],
            "updated_at": record["captured_at"],
        }
        if self.fail_step in {"before_checkpoint", "checkpoint"}:
            self._recover_index()
            raise CommitStepError("CHECKPOINT_WRITE_FAILED", "injected checkpoint failure", jsonl_event_id=event_id)
        try:
            atomic_json(self.snapshot_path, snapshot, fail_during=self.fail_step == "during_checkpoint")
        except OSError as exc:
            self._recover_index()
            raise CommitStepError("CHECKPOINT_WRITE_FAILED", str(exc), jsonl_event_id=event_id) from exc
        if self.fail_step == "after_checkpoint":
            self._recover_index()
            raise CommitStepError(
                "POST_CHECKPOINT_INTERRUPTED",
                "injected interruption after checkpoint",
                jsonl_event_id=event_id,
            )

        self._write_recent_pointer(record)
        self.sequence = int(record["sequence"])
        self.previous_hash = str(record["record_hash"])
        self.barcodes.add(str(record["barcode_normalized"]))
        if cmd.idempotency_key:
            self.idempotency_map[cmd.idempotency_key] = {"record_id": record["record_id"], "receipt_id": None}

        derivatives: dict[str, str] = {}
        for kind, function, path in (
            ("csv", append_csv, self.session_dir / "records.csv"),
            ("xlsx", append_xlsx, self.session_dir / "records.xlsx"),
        ):
            try:
                if self.fail_step == f"{kind}_export":
                    raise OSError(f"injected {kind} export failure")
                function(path, record)
                derivatives[kind] = "updated"
            except Exception as exc:
                derivatives[kind] = "pending_sync"
                atomic_json(
                    self.pending_dir / f"{record['record_id']}.{kind}.json",
                    {
                        "pending_sync_receipt_id": str(uuid.uuid4()),
                        "record_id": record["record_id"],
                        "target": str(path),
                        "error_class": type(exc).__name__,
                        "created_at": now_rfc3339(),
                    },
                )

        receipt = CommitReceipt.create(
            str(record["record_id"]),
            [str(self.records_path), str(individual), str(self.snapshot_path)],
            str(record["record_hash"]),
            derivatives,
            jsonl_event_id=event_id,
            individual_record_path=str(individual),
            checkpoint_version=int(record["sequence"]),
            net_g=net,
        )
        receipt_data = receipt.to_dict()
        receipt_data["recent_run_pointer"] = str(self.recent_pointer_path) if self.recent_pointer_path else None
        receipt_data["directory_fsync_supported"] = self.directory_fsync_supported
        if self.fail_step == "before_receipt":
            self._recover_index()
            raise CommitStepError(
                "COMMIT_RECEIPT_WRITE_FAILED",
                "injected interruption before receipt",
                jsonl_event_id=event_id,
            )
        atomic_json(self.receipts_dir / f"{receipt.receipt_id}.json", receipt_data)
        if cmd.idempotency_key:
            self.idempotency_map[cmd.idempotency_key]["receipt_id"] = receipt.receipt_id
        self.recovery_required = False
        return record, receipt

    def _quarantine_temp_files(self) -> list[str]:
        quarantined: list[str] = []
        for tmp in list(self.session_dir.rglob("*.tmp")):
            self.quarantine_dir.mkdir(parents=True, exist_ok=True)
            target = self.quarantine_dir / f"{tmp.name}.{uuid.uuid4().hex}.partial"
            shutil.move(str(tmp), str(target))
            quarantined.append(str(target))
        return quarantined

    def _synthesize_missing_receipts(self, rows: list[dict[str, Any]]) -> int:
        existing: set[str] = set()
        for path in self.receipts_dir.glob("*.json") if self.receipts_dir.exists() else []:
            try:
                existing.add(str(json.load(path.open(encoding="utf-8")).get("record_id")))
            except Exception:
                continue
        created = 0
        for row in rows:
            if str(row["record_id"]) in existing:
                continue
            individual = self.records_dir / f"{int(row['sequence']):06d}_{row['record_id']}.json"
            if not individual.exists() or not self.snapshot_path.exists():
                continue
            receipt = CommitReceipt.create(
                str(row["record_id"]),
                [str(self.records_path), str(individual), str(self.snapshot_path)],
                str(row["record_hash"]),
                {"csv": "recovery_review", "xlsx": "recovery_review"},
                jsonl_event_id=str(row["event_id"]),
                individual_record_path=str(individual),
                checkpoint_version=int(row["sequence"]),
                net_g=float(row["net_g"]),
            )
            data = receipt.to_dict()
            data["receipt_origin"] = "recovery_synthesized_from_authoritative_ledger"
            atomic_json(self.receipts_dir / f"{receipt.receipt_id}.json", data)
            created += 1
        return created

    def recover_from_ledger(self) -> dict[str, Any]:
        tail = getattr(self, "startup_tail_repair", None) or quarantine_incomplete_jsonl_tail(self.records_path, self.quarantine_dir)
        quarantined_temps = self._quarantine_temp_files()
        ok, reason = self.verify_chain()
        if not ok:
            raise ValueError(f"ledger chain invalid: {reason}")
        rows = [row for row in parse_jsonl(self.records_path) if row.get("event_type") == "weight_record"]
        rebuilt_records = 0
        for row in rows:
            path = self.records_dir / f"{int(row['sequence']):06d}_{row['record_id']}.json"
            if not path.exists():
                atomic_json(path, row)
                rebuilt_records += 1
        checkpoint_rebuilt = 0
        if rows:
            last = rows[-1]
            snapshot = {
                "schema_version": "1.0.0",
                "session_id": self.context.session_id,
                "run_id": self.context.run_id,
                "checkpoint_version": last["sequence"],
                "last_sequence": last["sequence"],
                "last_record_id": last["record_id"],
                "last_record_hash": last["record_hash"],
                "record_count": len(rows),
                "updated_at": now_rfc3339(),
            }
            current = None
            try:
                current = json.load(self.snapshot_path.open(encoding="utf-8"))
            except Exception:
                pass
            if not current or int(current.get("last_sequence", 0)) != int(last["sequence"]):
                atomic_json(self.snapshot_path, snapshot)
                checkpoint_rebuilt = 1
            self._write_recent_pointer(last)
        receipts_rebuilt = self._synthesize_missing_receipts(rows)
        receipt = {
            "receipt_id": f"recovery-{uuid.uuid4()}",
            "status": "recovered",
            "session_id": self.context.session_id,
            "ledger_valid": True,
            "records_seen": len(rows),
            "individual_records_rebuilt": rebuilt_records,
            "checkpoint_rebuilt_count": checkpoint_rebuilt,
            "commit_receipts_rebuilt": receipts_rebuilt,
            "temporary_files_quarantined": quarantined_temps,
            "jsonl_tail_repair": tail,
            "last_committed_record_id": rows[-1]["record_id"] if rows else None,
            "uncommitted_weight_restored": False,
            "created_at": now_rfc3339(),
        }
        atomic_json(self.recovery_dir / f"{receipt['receipt_id']}.json", receipt)
        self._recover_index()
        self.recovery_required = False
        return receipt

    def finish(self) -> dict[str, Any]:
        manifest = json.load(self.manifest_path.open(encoding="utf-8"))
        if manifest.get("status") == "finished":
            return manifest
        manifest["status"] = "finished"
        manifest["finished_at"] = now_rfc3339()
        manifest["final_sequence"] = self.sequence
        atomic_json(self.manifest_path, manifest)
        self.append_event(
            {
                "event_type": "run_finished",
                "session_id": self.context.session_id,
                "run_id": self.context.run_id,
                "final_sequence": self.sequence,
            }
        )
        return manifest

    def append_event(self, event: dict[str, Any]) -> dict[str, Any]:
        value = dict(event)
        value.setdefault("created_at", now_rfc3339())
        value.setdefault("event_id", str(uuid.uuid4()))
        with self.records_path.open("a", encoding="utf-8") as handle:
            handle.write(canonical(value) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return value
