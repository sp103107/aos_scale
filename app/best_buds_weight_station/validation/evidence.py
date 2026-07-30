from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
from typing import Any


def atomic_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_receipt(repo_root: Path, lane: str, data: dict[str, Any], run_id: str = "latest") -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in run_id)
    return atomic_json(repo_root / f"validation/receipts/{lane}.{safe}.json", data)
