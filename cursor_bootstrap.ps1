param([string]$Plan = "cursor_ready", [string]$RunId = "cursor-ready-v0.1.10")
$ErrorActionPreference = 'Stop'; Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 scripts/launcher.py stage run-plan --plan $Plan --run-id $RunId @args }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python scripts/launcher.py stage run-plan --plan $Plan --run-id $RunId @args }
else { throw 'Python 3.11 or 3.12 is required.' }
exit $LASTEXITCODE
