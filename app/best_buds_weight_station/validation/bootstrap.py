from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..models import now_rfc3339
from .evidence import atomic_json
from .harness import ValidationHarness

PREHARDWARE_LANES = [
    "repository-inspection",
    "development-hygiene",
    "software",
    "agent-entrypoint",
    "software-dry-run",
    "recovery-matrix",
    "frontend-smoke",
    "packaging-preflight",
]

OPERATOR_READY_LANES = [
    "repository-inspection",
    "development-hygiene",
    "software",
    "launchers",
    "agent-entrypoint",
    "software-dry-run",
    "recovery-matrix",
    "operator-runtime",
    "scripted-device",
    "frontend-smoke",
    "windows-packaging-source",
    "linux-parity",
    "packaging-preflight",
]


@dataclass
class BootstrapResult:
    run_id: str
    version: str
    profile: str
    status: str
    lanes: list[dict[str, Any]]
    repo_root: str
    next_phase: str
    next_command: str
    physical_gates: dict[str, str]
    warnings: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=now_rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentBootstrap:
    """Deterministic software-only bootstrap for Cursor, Codex, and CI agents."""

    def __init__(self, repo_root: Path | None = None, *, persist: bool = True):
        self.harness = ValidationHarness(repo_root, persist_receipts=False)
        self.repo_root = self.harness.repo_root
        self.persist = persist

    def run(
        self,
        *,
        profile: str = "prehardware",
        include_ui: bool = True,
        run_id: str | None = None,
    ) -> BootstrapResult:
        run_id = run_id or f"bootstrap-{uuid.uuid4().hex[:12]}"
        prior: dict[str, dict[str, Any]] = {}
        results: list[dict[str, Any]] = []
        warnings: list[str] = []

        lanes = list(OPERATOR_READY_LANES if profile == "operator-ready" else PREHARDWARE_LANES)
        if not include_ui:
            if "frontend-smoke" in lanes:
                lanes.remove("frontend-smoke")

        for lane in lanes:
            result = self.harness.run_lane(
                lane,
                profile,
                options={"bootstrap_run_id": run_id},
                prior=prior,
            )
            data = result.to_dict()
            prior[lane] = data
            results.append(data)
            warnings.extend(data.get("warnings", []))
            if result.status == "FAIL":
                break

        failures = [item for item in results if item["status"] == "FAIL"]
        blockers = [item for item in results if item["status"] in {"BLOCKED", "NOT_RUN"}]
        status = "FAIL" if failures else ("PASS_WITH_WARNINGS" if blockers or warnings else "PASS")
        next_command = (
            "python -m best_buds_weight_station.validation run --lane firmware "
            "--profile integration --port <serial-port>"
        )
        result = BootstrapResult(
            run_id=run_id,
            version=self.harness.version,
            profile=profile,
            status=status,
            lanes=results,
            repo_root=str(self.repo_root),
            next_phase="rc3d_uno_r3_hx711_physical_scale_bringup" if profile == "operator-ready" else "rc3c_hardware_inventory_wiring_and_physical_integration",
            next_command=next_command,
            physical_gates={
                "firmware_compile_upload": "NOT_RUN",
                "physical_serial": "NOT_RUN",
                "zero_tare": "NOT_RUN",
                "calibration": "NOT_RUN",
                "physical_loop": "NOT_RUN",
            },
            warnings=sorted(set(warnings)),
        )
        if self.persist:
            receipt_root = self.repo_root / "validation" / "receipts" / "bootstrap" / run_id
            for lane_result in results:
                atomic_json(receipt_root / f"{lane_result['lane']}.json", lane_result)
            target = self.repo_root / "validation" / "reports" / f"agent_bootstrap.{run_id}.json"
            atomic_json(target, result.to_dict())
            atomic_json(self.repo_root / "validation" / "reports" / "agent_bootstrap.latest.json", result.to_dict())
        return result


def run_agent_bootstrap(
    repo_root: Path | None = None,
    *,
    profile: str = "prehardware",
    include_ui: bool = True,
    persist: bool = True,
    run_id: str | None = None,
) -> dict[str, Any]:
    return AgentBootstrap(repo_root, persist=persist).run(
        profile=profile,
        include_ui=include_ui,
        run_id=run_id,
    ).to_dict()


def main() -> int:
    print(json.dumps(run_agent_bootstrap(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
