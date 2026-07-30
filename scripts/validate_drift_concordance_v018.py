#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
CURRENT = [
    "README.md", "CHANGELOG.md", "docs/SYSTEM_STATE_CURRENT.md", "docs/WINDOWS_BUILD.md", "docs/DEBIAN_INSTALL.md",
    "docs/WINDOWS_FIRST_OPERATOR_APPLICATION_V0.1.9.md", "docs/FINAL_POLISH_AND_DRIFT_REVIEW_V0.1.9.md",
    "docs/CORE_PROCESS_IMPLEMENTATION_CURRENT.md", "repo_release_state.json", "guide_pack.json",
    "backend/backend_manifest.v0.1.9.json", "frontend/frontend_manifest.v0.1.9.json", "frontend/design_tokens.v0.1.9.json",
    "release_candidate/rc_phase_matrix.v0.1.9.json", "cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_9.md",
    "context/working_set/working_set_update_0010.json", "context/episodes/episode_0010_v0.1.9.json",
    "context/resume_pack/resume_pack_manifest.v0.1.9.json", "pipeline/stage_catalog.v0.1.9.json",
    "pipeline/plans/cursor_ready.v0.1.9.json", "entrypoints/surface_entry_map.v0.1.9.json",
    "registry/surface_entry_registry.v0.1.9.json", "pods/best_buds_weight_station_pod_manifest.v0.1.9.json",
    "runtime/evidence_index.v0.1.9.json",
]

def main() -> int:
    issues = []
    for rel in CURRENT:
        path = ROOT / rel
        if not path.exists():
            issues.append({"code": "CURRENT_MISSING", "path": rel})
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if VERSION not in text:
            issues.append({"code": "CURRENT_VERSION_MISSING", "path": rel})
    # Unversioned current anchors may mention the previous version only when explicitly labeled as previous/source.
    for rel in ["README.md", "docs/SYSTEM_STATE_CURRENT.md", "docs/WINDOWS_BUILD.md", "docs/DEBIAN_INSTALL.md", "repo_release_state.json", "guide_pack.json"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for old in ("0.1.3", "0.1.4", "0.1.5", "0.1.6"):
            if re.search(rf"(?i)(current|version|package)\D{{0,25}}{re.escape(old)}", text):
                issues.append({"code": "STALE_CURRENT_REFERENCE", "path": rel, "value": old})
    if list((ROOT / "app").glob("*.egg-info")):
        issues.append({"code": "GENERATED_EGG_INFO_PRESENT", "path": "app/"})
    if "_LegacyCallbackNamesForContract" in (ROOT / "app/best_buds_weight_station/production_ui.py").read_text():
        issues.append({"code": "DEAD_CONTRACT_STUB_PRESENT", "path": "app/best_buds_weight_station/production_ui.py"})
    matrix = json.loads((ROOT / "release_candidate/rc_phase_matrix.v0.1.9.json").read_text())
    phase_names = [item["phase"] for item in matrix["phases"]]
    if len(phase_names) != len(set(phase_names)):
        issues.append({"code": "DUPLICATE_PHASE_ID", "path": "release_candidate/rc_phase_matrix.v0.1.9.json"})
    for path in (ROOT / "pipeline/stages").glob("*.json"):
        data = json.loads(path.read_text())
        if data.get("version") != VERSION:
            issues.append({"code": "STAGE_VERSION_DRIFT", "path": path.relative_to(ROOT).as_posix()})
        serialized = json.dumps(data)
        if any(old in serialized for old in ["test_operator_runtime_v016.py", "test_device_service_v013.py", "file_manifest.v0.1.6.json"]):
            issues.append({"code": "ACTIVE_STAGE_LEGACY_REFERENCE", "path": path.relative_to(ROOT).as_posix()})
    manifest = json.loads((ROOT / "frontend/frontend_manifest.v0.1.9.json").read_text())
    if manifest.get("tk_runtime") != "PASS":
        issues.append({"code": "FRONTEND_RUNTIME_STATUS_DRIFT", "path": "frontend/frontend_manifest.v0.1.9.json"})
    historical = list((ROOT / "context/episodes").glob("episode_*_v0.1.[0-7].json")) + list((ROOT / "manifests").glob("file_manifest.v0.1.[0-7].json"))
    report = {
        "version": VERSION,
        "status": "PASS" if not issues else "FAIL",
        "current_surface_count": len(CURRENT),
        "historical_immutable_count": len(historical),
        "compatibility_policy": "older references are allowed only in immutable history or explicit compatibility surfaces",
        "issues": issues,
    }
    out = ROOT / f"reports/drift_concordance_report.v{VERSION}.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
