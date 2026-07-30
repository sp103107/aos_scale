$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $Root
python -m pip install --upgrade pip
python -m pip install -e '.[desktop,serial,dev]' pyinstaller
python -m pytest -q
python scripts\validate_launchers.py
python scripts\validate_frontend_runtime_truth.py
python -m PyInstaller --clean --noconfirm packaging\windows\BestBudsWeightStation.spec
& packaging\windows\verify_windows.ps1
New-Item -ItemType Directory -Force -Path dist\windows | Out-Null
Compress-Archive -Force dist\BestBudsWeightStation dist\windows\BestBudsWeightStation-windows-x64-v0.1.7.zip
