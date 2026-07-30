"""PyInstaller entrypoint (absolute imports; safe for frozen EXE)."""

from best_buds_weight_station.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
