from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .models import RunContext, now_rfc3339
from .reports import compile_report
from .settings import SettingsStore
from .storage import SessionStore, atomic_json, safe_component
from .version import __version__

RUN_SCHEMA_VERSION = "1.0.0"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass
class RunDefinition:
    run_id: str
    operator_id: str
    facility_id: str
    station_id: str
    cultivars: list[dict[str, str]]
    capture_mode: str = "manual"
    unit: str = "g"
    container_id: str = "DEFAULT"
    tare_g: float = 0.0
    measurement_stage: str = "harvest"
    weight_purpose: str = "wet_weight"
    stability_profile_id: str = "standard_hanging_grams"
    maximum_capacity_g: float = 10000.0
    session_id: str | None = None
    created_at: str = field(default_factory=now_rfc3339)

    def validate(self) -> None:
        for label in ("run_id", "operator_id", "facility_id", "station_id", "container_id"):
            raw_value = getattr(self, label)
            if not isinstance(raw_value, str):
                raise ValueError(f"invalid {label}")
            value = raw_value.strip()
            safe_component(value, label)
            if not _IDENTIFIER.fullmatch(value):
                raise ValueError(f"invalid {label}")
        if self.capture_mode not in {"automatic", "manual"}:
            raise ValueError("invalid capture mode")
        if self.unit != "g":
            raise ValueError("only grams are supported")
        if not self.cultivars:
            raise ValueError("at least one cultivar is required")
        normalized: set[str] = set()
        for item in self.cultivars:
            if not isinstance(item.get("cultivar_id"), str) or not isinstance(item.get("name"), str):
                raise ValueError("invalid cultivar roster")
            cultivar_id = item["cultivar_id"].strip()
            name = item["name"].strip()
            if not cultivar_id or not name or not _IDENTIFIER.fullmatch(cultivar_id):
                raise ValueError("invalid cultivar roster")
            if cultivar_id.lower() in normalized:
                raise ValueError("duplicate cultivar identifier")
            normalized.add(cultivar_id.lower())
        if float(self.tare_g) < 0 or float(self.maximum_capacity_g) <= 0:
            raise ValueError("invalid weight bounds")

    def to_context(self, *, evidence_truth_class: str) -> RunContext:
        self.validate()
        cultivar = self.cultivars[0]
        return RunContext(
            session_id=self.session_id or str(uuid.uuid4()),
            run_id=self.run_id,
            operator_id=self.operator_id,
            facility_id=self.facility_id,
            station_id=self.station_id,
            cultivar_id=cultivar["cultivar_id"],
            cultivar_raw_name=cultivar["name"],
            cultivar_normalized_name=" ".join(cultivar["name"].split()),
            container_id=self.container_id,
            tare_g=float(self.tare_g),
            stability_profile_id=self.stability_profile_id,
            evidence_truth_class=evidence_truth_class,
            measurement_stage=self.measurement_stage,
            weight_purpose=self.weight_purpose,
        )


@dataclass
class LoadedRun:
    definition: RunDefinition
    store: SessionStore
    manifest_path: Path


class RunManager:
    def __init__(self, settings_store: SettingsStore):
        self.settings_store = settings_store

    def _root(self, data_root: str | Path | None = None) -> Path:
        if data_root is None:
            data_root = self.settings_store.load().data_root
        return self.settings_store.validate_data_root(data_root)

    def create(self, definition: RunDefinition, *, data_root: str | Path | None = None,
               evidence_truth_class: str = "NOT_RUN") -> LoadedRun:
        definition.validate()
        root = self._root(data_root)
        session_id = definition.session_id or f"{definition.run_id}-{uuid.uuid4().hex[:8]}"
        definition.session_id = session_id
        target = root / "sessions" / safe_component(session_id, "session_id")
        if target.exists() and any(target.iterdir()):
            raise FileExistsError("run session already exists; no files were overwritten")
        context = definition.to_context(evidence_truth_class=evidence_truth_class)
        store = SessionStore(root, context, recent_pointer_path=self.settings_store.recent_run_path)
        manifest = json.load(store.manifest_path.open(encoding="utf-8"))
        manifest.update({
            "schema_version": RUN_SCHEMA_VERSION,
            "application_version": __version__,
            "run_definition": asdict(definition),
            "status": "active",
        })
        atomic_json(store.manifest_path, manifest)
        self.settings_store.write_recent_run({
            "session_id": context.session_id,
            "run_id": context.run_id,
            "session_manifest": str(store.manifest_path),
            "data_root": str(root),
            "last_sequence": 0,
            "last_record_id": None,
        })
        return LoadedRun(definition, store, store.manifest_path)

    @staticmethod
    def _manifest_path(selection: str | Path) -> Path:
        path = Path(selection).expanduser().resolve()
        if path.is_dir():
            path = path / "session_manifest.json"
        elif path.name == "records.jsonl":
            path = path.parent / "session_manifest.json"
        if path.name != "session_manifest.json":
            raise ValueError("select a run folder, session manifest, or authoritative records.jsonl")
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("run manifest not found")
        return path

    def load(self, selection: str | Path, *, require_active: bool = True) -> LoadedRun:
        manifest_path = self._manifest_path(selection)
        manifest = json.load(manifest_path.open(encoding="utf-8"))
        if manifest.get("schema_version") not in {None, RUN_SCHEMA_VERSION}:
            raise ValueError("unsupported run manifest version")
        if require_active and manifest.get("status") == "finished":
            raise ValueError("run is finished and cannot be resumed")
        definition_data = manifest.get("run_definition")
        if not isinstance(definition_data, dict):
            # Backward-compatible conversion from v0.1.2 context.
            context_data = manifest.get("context") or {}
            definition_data = {
                "run_id": context_data.get("run_id"),
                "operator_id": context_data.get("operator_id"),
                "facility_id": context_data.get("facility_id"),
                "station_id": context_data.get("station_id"),
                "cultivars": [{
                    "cultivar_id": context_data.get("cultivar_id"),
                    "name": context_data.get("cultivar_raw_name") or context_data.get("cultivar_normalized_name"),
                }],
                "capture_mode": "manual",
                "unit": "g",
                "container_id": context_data.get("container_id", "DEFAULT"),
                "tare_g": context_data.get("tare_g", 0.0),
                "session_id": context_data.get("session_id"),
            }
        allowed = RunDefinition.__dataclass_fields__
        definition = RunDefinition(**{key: value for key, value in definition_data.items() if key in allowed})
        definition.validate()
        root = manifest_path.parents[2]
        context_data = manifest.get("context") or definition.to_context(evidence_truth_class="NOT_RUN").__dict__
        context = RunContext(**{key: context_data[key] for key in RunContext.__dataclass_fields__ if key in context_data})
        store = SessionStore(root, context, recent_pointer_path=self.settings_store.recent_run_path)
        ok, reason = store.verify_chain()
        if not ok:
            raise ValueError(f"run ledger validation failed: {reason}")
        self.settings_store.write_recent_run({
            "session_id": context.session_id,
            "run_id": context.run_id,
            "session_manifest": str(manifest_path),
            "data_root": str(root),
            "last_sequence": store.sequence,
            "last_record_id": self._last_record_id(store),
        })
        return LoadedRun(definition, store, manifest_path)

    def resume_latest(self) -> LoadedRun:
        pointer = self.settings_store.read_recent_run()
        return self.load(pointer["session_manifest"])

    @staticmethod
    def _last_record_id(store: SessionStore) -> str | None:
        try:
            value = json.load(store.snapshot_path.open(encoding="utf-8"))
        except Exception:
            return None
        return value.get("last_record_id")

    def finish(self, loaded: LoadedRun) -> dict[str, Any]:
        return loaded.store.finish()

    def export(self, loaded: LoadedRun, destination: str | Path) -> dict[str, Any]:
        destination_path = Path(destination).expanduser().resolve()
        destination_path.mkdir(parents=True, exist_ok=True)
        report = compile_report(loaded.store.session_dir)
        source = Path(report["json_path"])
        target = destination_path / source.name
        target.write_bytes(source.read_bytes())
        return {"status": "exported", "authoritative": False, "path": str(target), "report": report}
