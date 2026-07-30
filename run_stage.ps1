param([Parameter(Mandatory=$true)][string]$Stage, [string]$RunId = "manual-stage")
$ErrorActionPreference='Stop'; Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 scripts/launcher.py stage run --stage $Stage --run-id $RunId @args } else { & python scripts/launcher.py stage run --stage $Stage --run-id $RunId @args }
exit $LASTEXITCODE
