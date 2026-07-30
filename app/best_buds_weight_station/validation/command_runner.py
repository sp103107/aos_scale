from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


def run_command(command: list[str], cwd: Path, timeout: int = 300) -> dict[str, Any]:
    """Run one validator with bounded, file-backed output.

    File-backed streams prevent child and GUI descendants from retaining a
    parent pipe, which makes the coding-agent bootstrap deterministic on both
    Windows and Linux automation hosts.
    """
    started = time.monotonic()
    env = {
        **os.environ,
        "PYTHONPATH": str(cwd / "app"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "DD_TRACE_ENABLED": "false",
        "DD_TRACE_STARTUP_LOGS": "false",
    }
    with tempfile.TemporaryDirectory(prefix="bbws-validation-command-") as td:
        stdout_path = Path(td) / "stdout.log"
        stderr_path = Path(td) / "stderr.log"
        with stdout_path.open("w+", encoding="utf-8") as stdout, stderr_path.open("w+", encoding="utf-8") as stderr:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                text=True,
                stdout=stdout,
                stderr=stderr,
                env=env,
                start_new_session=(os.name != "nt"),
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
            )
            timed_out = False
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "nt":
                    process.kill()
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
            stdout.flush(); stderr.flush()
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
    if timed_out:
        stderr_text = (stderr_text + "\ntimeout").strip()
    return {
        "command": command,
        "exit_code": 124 if timed_out else process.returncode,
        "stdout": stdout_text[-20000:],
        "stderr": stderr_text[-20000:],
        "duration_seconds": round(time.monotonic() - started, 3),
    }
