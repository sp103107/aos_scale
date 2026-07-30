$ErrorActionPreference = 'Stop'
$Target = Join-Path $env:LOCALAPPDATA 'BestBudsWeightStation\app'
$ShortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Best Buds Weight Station.lnk'
if (Test-Path $ShortcutPath) { Remove-Item -Force $ShortcutPath }
if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
Write-Host 'Application files removed. Run data under BestBudsWeightStation\runs is preserved.'
