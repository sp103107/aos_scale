$ErrorActionPreference = 'Stop'
$InstallRoot = Join-Path $env:LOCALAPPDATA 'BestBudsWeightStation'
$Target = Join-Path $InstallRoot 'app'

$Desktop = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Best Buds Weight Station.lnk'
if (Test-Path $Desktop) { Remove-Item -Force $Desktop }

$Programs = [Environment]::GetFolderPath('Programs')
$StartMenuDir = Join-Path $Programs 'Best Buds Cultivator Weight Station'
if (Test-Path $StartMenuDir) { Remove-Item -Recurse -Force $StartMenuDir }

if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }

Write-Host 'Application files and shortcuts removed.'
Write-Host "Run data under $(Join-Path $InstallRoot 'runs') is preserved when present."
