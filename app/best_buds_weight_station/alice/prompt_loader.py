from __future__ import annotations
from pathlib import Path

PROMPT_NAMES = {
    "system": "ALICE_SYSTEM_PROMPT.md",
    "harvest_start": "ALICE_HARVEST_START_PROMPT.md",
    "capture": "ALICE_CAPTURE_PROMPT.md",
    "recovery": "ALICE_RECOVERY_PROMPT.md",
    "validation": "ALICE_VALIDATION_PROMPT.md",
    "non_claim": "ALICE_NON_CLAIM_POLICY.md",
}


def prompt_root() -> Path:
    return Path(__file__).parents[3] / "prompts" / "alice"


def load_prompt(name: str) -> str:
    if name not in PROMPT_NAMES:
        raise KeyError(f"Unknown Alice prompt: {name}")
    path = prompt_root() / PROMPT_NAMES[name]
    return path.read_text(encoding="utf-8")
