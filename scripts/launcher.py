from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def venv_python(env_dir: Path) -> Path:
    return env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def ensure_environment(root: Path, *, install: bool) -> Path:
    env_dir = root / ".venv"
    python = venv_python(env_dir)
    if not python.exists():
        venv.EnvBuilder(with_pip=True, clear=False).create(env_dir)
    if install:
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-e", ".[desktop,serial]"], cwd=root, check=True)
    return python


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cross-platform repository launcher")
    parser.add_argument("mode", choices=("launch", "simulator", "bootstrap", "validation", "stage"))
    parser.add_argument("--no-install", action="store_true")
    parser.add_argument("--direct", action="store_true", help="Use the current Python without creating a virtual environment")
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved command without executing it")
    args, passthrough = parser.parse_known_args(argv)
    root = repository_root()
    logs = root / "logs"; logs.mkdir(exist_ok=True)
    try:
        python = Path(sys.executable) if args.direct else ensure_environment(root, install=not args.no_install)
        if args.mode == "launch":
            command = [str(python), "-m", "best_buds_weight_station", *passthrough]
        elif args.mode == "simulator":
            command = [str(python), "-m", "best_buds_weight_station", "--simulator", *passthrough]
        elif args.mode == "bootstrap":
            command = [str(python), "-m", "best_buds_weight_station.bootstrap", "--profile", "operator-ready", *passthrough]
        elif args.mode == "validation":
            command = [str(python), "-m", "best_buds_weight_station.validation", *passthrough]
        else:
            command = [str(python), "-m", "best_buds_weight_station.stage_runner", *passthrough]
        if args.dry_run:
            print(" ".join(command))
            return 0
        env = os.environ.copy()
        if args.direct:
            env["PYTHONPATH"] = str(root / "app") + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        with (logs / f"launcher-{args.mode}.log").open("a", encoding="utf-8") as log:
            log.write("COMMAND: " + " ".join(command) + "\n")
            log.flush()
            completed = subprocess.run(command, cwd=root, env=env)
            log.write(f"EXIT_CODE: {completed.returncode}\n")
        return completed.returncode
    except subprocess.CalledProcessError as exc:
        print(f"Environment bootstrap failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 2
    except Exception as exc:
        print(f"Launcher failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
