$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $Root
$Exe = Join-Path $Root 'dist\BestBudsWeightStation\BestBudsWeightStation.exe'
if (-not (Test-Path $Exe)) { throw "Windows artifact not found: $Exe" }
& $Exe --version
if ($LASTEXITCODE -ne 0) { throw 'Version smoke failed.' }
& $Exe --self-test --simulator
if ($LASTEXITCODE -ne 0) { throw 'Simulator self-test failed.' }
Write-Host 'Windows source and packaged executable smoke completed.'
