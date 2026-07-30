$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$Source = Join-Path $Root 'dist\BestBudsWeightStation'
$Target = Join-Path $env:LOCALAPPDATA 'BestBudsWeightStation\app'
if (-not (Test-Path $Source)) { throw 'Build the Windows package first.' }
New-Item -ItemType Directory -Force -Path $Target | Out-Null
Copy-Item -Recurse -Force (Join-Path $Source '*') $Target
$ShortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Best Buds Weight Station.lnk'
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $Target 'BestBudsWeightStation.exe'
$Shortcut.WorkingDirectory = $Target
$Shortcut.Save()
Write-Host "Installed to $Target"
