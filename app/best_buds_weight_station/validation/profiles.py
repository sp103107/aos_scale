from __future__ import annotations
import json
from pathlib import Path

def profile_root(repo_root: Path) -> Path:
    return repo_root / "validation" / "profiles"

def load_profile(repo_root: Path, name: str) -> dict:
    path=profile_root(repo_root)/f"{name}.profile.json"
    if not path.exists(): raise FileNotFoundError(f"unknown validation profile: {name}")
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("profile") != name: raise ValueError("profile identity mismatch")
    return data
