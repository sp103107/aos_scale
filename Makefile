# Best Buds / aos_scale — common developer targets
PYTHON ?= python
export PYTHONPATH := app

.PHONY: help install install-dev test validate release-check clean windows-build

help:
	@echo "Targets:"
	@echo "  install        Install package runtime deps"
	@echo "  install-dev    Install package + desktop + dev deps"
	@echo "  test           Run pytest"
	@echo "  validate       Run scripts/validate_repo.py"
	@echo "  release-check  test + validate"
	@echo "  windows-build  Native Windows PyInstaller + Setup (PowerShell)"
	@echo "  clean          Remove caches and build artifacts"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,desktop]"

test:
	$(PYTHON) -m pytest -q

validate:
	$(PYTHON) scripts/validate_repo.py

release-check: test validate

windows-build:
	@powershell -NoProfile -ExecutionPolicy Bypass -File packaging/windows/build_windows.ps1

clean:
	$(PYTHON) -c "import pathlib,shutil; root=pathlib.Path('.'); [shutil.rmtree(p, ignore_errors=True) for p in root.rglob('__pycache__')]; [shutil.rmtree(root/p, ignore_errors=True) for p in ('.pytest_cache','build')]"
