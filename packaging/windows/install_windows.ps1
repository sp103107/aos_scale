$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$Source = Join-Path $Root 'dist\BestBudsWeightStation'
$InstallRoot = Join-Path $env:LOCALAPPDATA 'BestBudsWeightStation'
$Target = Join-Path $InstallRoot 'app'
if (-not (Test-Path $Source)) { throw 'Build the Windows package first (packaging\windows\build_windows.ps1).' }

New-Item -ItemType Directory -Force -Path $Target | Out-Null
Copy-Item -Recurse -Force (Join-Path $Source '*') $Target

$Exe = Join-Path $Target 'BestBudsWeightStation.exe'
$Shell = New-Object -ComObject WScript.Shell

$Desktop = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Best Buds Weight Station.lnk'
$DesktopShortcut = $Shell.CreateShortcut($Desktop)
$DesktopShortcut.TargetPath = $Exe
$DesktopShortcut.WorkingDirectory = $Target
$DesktopShortcut.Save()

$Programs = [Environment]::GetFolderPath('Programs')
$StartMenuDir = Join-Path $Programs 'Best Buds Cultivator Weight Station'
New-Item -ItemType Directory -Force -Path $StartMenuDir | Out-Null
$StartMenu = Join-Path $StartMenuDir 'Best Buds Weight Station.lnk'
$StartShortcut = $Shell.CreateShortcut($StartMenu)
$StartShortcut.TargetPath = $Exe
$StartShortcut.WorkingDirectory = $Target
$StartShortcut.Save()

Write-Host "Installed to $Target"
Write-Host "Desktop shortcut: $Desktop"
Write-Host "Start Menu: $StartMenu"
Write-Host "Run data folder (created on first run): $(Join-Path $InstallRoot 'runs')"
