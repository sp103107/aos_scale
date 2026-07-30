param([Parameter(Mandatory=$true)][string]$RunId, [string]$Plan = "cursor_ready")
$ErrorActionPreference='Stop'; Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 scripts/launcher.py stage resume --run-id $RunId --plan $Plan @args } else { & python scripts/launcher.py stage resume --run-id $RunId --plan $Plan @args }
exit $LASTEXITCODE
