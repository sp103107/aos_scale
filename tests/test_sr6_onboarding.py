"""BBWS SR6 onboarding + version contract tests."""
from pathlib import Path

from best_buds_weight_station.onboard import build_guidance, main as onboard_main
from best_buds_weight_station.version import __version__

ROOT = Path(__file__).parents[1]


def test_product_version_is_current_rc():
    assert __version__ == "2.0.0-rc4"


def test_start_here_doors_exist():
    assert (ROOT / "START_HERE.md").exists()
    assert (ROOT / "START_HERE_CODING_AGENT.md").exists()
    assert (ROOT / "docs" / "OPERATOR_ONBOARDING.md").exists()
    assert (ROOT / "docs" / "INTENDED_USER.md").exists()
    # Docs must stay concordant with the live product version.
    assert __version__ in (ROOT / "START_HERE.md").read_text(encoding="utf-8")


def test_onboard_guidance_runtime_not_claimed():
    guidance = build_guidance(ROOT)
    assert guidance["runtime_claimed"] is False
    assert guidance["version"] == __version__
    assert (Path(guidance["repo_root"]) / "ACTIVE_ARC.yaml").exists()
    assert "ACTIVE_ARC.yaml" in guidance["load_order"][0]


def test_onboard_cli_exits_zero():
    assert onboard_main(["--version"]) == 0
    assert onboard_main(["--json"]) == 0
