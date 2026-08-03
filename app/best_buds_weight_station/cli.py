from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .reports import compile_report
from .selftest import run_self_test
from .version import __version__


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="best-buds-weight-station")
    p.add_argument("--version", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--simulator", action="store_true")
    p.add_argument("--data-root")
    p.add_argument("--compile-report")
    p.add_argument("--ui-smoke", action="store_true")
    p.add_argument("--smoke", action="store_true", help="alias for --ui-smoke")
    p.add_argument("--ui", choices=("auto", "pyside", "tk"), default="auto")
    p.add_argument("--capture-mode", choices=("automatic", "manual"), default="manual")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.self_test:
        try:
            print(json.dumps(run_self_test(), indent=2, sort_keys=True))
            return 0
        except Exception as exc:
            print(json.dumps({"status": "fail", "error": str(exc)}), file=sys.stderr)
            return 1
    if args.compile_report:
        try:
            print(json.dumps(compile_report(Path(args.compile_report)), indent=2, sort_keys=True))
            return 0
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
    smoke = bool(args.ui_smoke or args.smoke)
    try:
        if args.ui == "tk":
            from .production_ui import launch_tk

            return int(launch_tk(args.data_root, args.simulator, smoke, args.capture_mode) or 0)
        from .ui import launch

        return int(launch(args.data_root, args.simulator, smoke, args.capture_mode) or 0)
    except Exception as exc:
        print(f"Launch failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
