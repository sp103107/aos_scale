$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $Root
$Exe = Join-Path $Root 'dist\BestBudsWeightStation\BestBudsWeightStation.exe'
if (-not (Test-Path $Exe)) { throw "Windows artifact not found: $Exe" }

function Invoke-PackagedSmoke {
    param([string[]]$ArgumentList, [string]$Label)
    $proc = Start-Process -FilePath $Exe -ArgumentList $ArgumentList -Wait -PassThru -NoNewWindow
    if ($null -eq $proc.ExitCode -or $proc.ExitCode -ne 0) {
        throw "$Label failed with exit code $($proc.ExitCode)"
    }
    Write-Host "$Label OK (exit $($proc.ExitCode))"
}

Invoke-PackagedSmoke -ArgumentList @('--version') -Label 'Version smoke'
Invoke-PackagedSmoke -ArgumentList @('--self-test', '--simulator') -Label 'Simulator self-test'

# Ensure the GUI subsystem process is fully released before zip/install steps.
Get-Process -Name 'BestBudsWeightStation' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host 'Windows source and packaged executable smoke completed.'
