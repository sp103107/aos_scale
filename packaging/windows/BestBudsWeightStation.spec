# PyInstaller spec executed only on a native Windows runner.
# Paths are resolved relative to the repo root (parent of packaging/).
from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# SPECPATH is normally the directory containing this .spec.
# Normalize if a caller ever passes the .spec file path instead.
_spec = Path(SPECPATH).resolve()
SPEC_DIR = _spec.parent if _spec.suffix.lower() == ".spec" else _spec
ROOT = SPEC_DIR.parents[1]
APP = ROOT / "app"
ENTRY = SPEC_DIR / "run_app.py"
if not ENTRY.is_file():
    raise SystemExit(f"PyInstaller entry not found: {ENTRY}")

hiddenimports = collect_submodules("PySide6")
datas = collect_data_files("PySide6")

a = Analysis(
    [str(ENTRY)],
    pathex=[str(APP)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BestBudsWeightStation",
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="BestBudsWeightStation",
)
