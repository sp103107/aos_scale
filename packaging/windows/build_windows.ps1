$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $Root

$Version = (Get-Content -Raw (Join-Path $Root 'VERSION')).Trim()
if (-not $Version) { throw 'VERSION file is empty or missing.' }

Write-Host "Building Best Buds Weight Station Windows package v$Version"

# Prefer project venv when present for a clean packaging environment.
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
if (Test-Path $VenvPython) {
    $Python = $VenvPython
    Write-Host "Using project venv: $Python"
} else {
    $Python = (Get-Command python -ErrorAction Stop).Source
    Write-Host "Using interpreter: $Python"
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -e '.[desktop,serial,dev]' pyinstaller
# PyInstaller rejects the obsolete pathlib backport if present on the interpreter.
cmd /c "`"$Python`" -m pip uninstall -y pathlib >nul 2>&1"
$global:LASTEXITCODE = 0

Write-Host 'Cleaning editable egg-info before tests...'
Get-ChildItem -Path (Join-Path $Root 'app') -Filter '*.egg-info' -Directory -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force

Write-Host 'Running packaging-critical pytest...'
$critical = @(
    'tests/test_device_service.py',
    'tests/test_operator_runtime.py',
    'tests/test_scale_control.py',
    'tests/test_usb_serial_settings.py',
    'tests/test_frontend_contract.py',
    'tests/test_frontend_polish.py'
) | Where-Object { Test-Path $_ }
& $Python -m pytest -q @critical
if ($LASTEXITCODE -ne 0) { throw "packaging-critical pytest failed with exit $LASTEXITCODE" }

Write-Host 'Soft-running full pytest (warn-first for historical drift/launcher checks)...'
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Full pytest exited $LASTEXITCODE (continuing packaging)."
}

# Warn-first: do not block packaging on obsolete launcher/repo validators.
foreach ($script in @('scripts\validate_launchers.py', 'scripts\validate_frontend_runtime_truth.py')) {
    if (Test-Path $script) {
        Write-Host "Soft-running $script (warn-first)..."
        & $Python $script
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "$script exited $LASTEXITCODE (continuing packaging)."
        }
    }
}

Write-Host 'Running PyInstaller...'
& $Python -m PyInstaller --clean --noconfirm packaging\windows\BestBudsWeightStation.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit $LASTEXITCODE" }

& (Join-Path $PSScriptRoot 'verify_windows.ps1')

$OutDir = Join-Path $Root 'dist\windows'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$ZipName = "BestBudsWeightStation-windows-x64-v$Version.zip"
$ZipPath = Join-Path $OutDir $ZipName
if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
$AppDir = Join-Path $Root 'dist\BestBudsWeightStation'
Get-Process -Name 'BestBudsWeightStation' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
# Prefer tar to avoid Compress-Archive file locks on Windows.
$Tar = Get-Command tar -ErrorAction SilentlyContinue
if ($Tar) {
    Push-Location (Join-Path $Root 'dist')
    try {
        & tar -a -cf $ZipPath 'BestBudsWeightStation'
        if ($LASTEXITCODE -ne 0) { throw "tar zip failed with exit $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
} else {
    Compress-Archive -Force -Path $AppDir -DestinationPath $ZipPath
}
Write-Host "Wrote $ZipPath"

$SetupPath = $null
$IsccCandidates = @(
    (Get-Command iscc -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
)
$IsccCandidates += @(Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter 'ISCC.exe' -Recurse -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName)
$Iscc = $IsccCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if ($Iscc) {
    Write-Host "Compiling Inno Setup installer with $Iscc"
    $Iss = Join-Path $PSScriptRoot 'BestBudsWeightStation.iss'
    & $Iscc "/DMyAppVersion=$Version" $Iss
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup compile failed with exit $LASTEXITCODE" }
    $SetupPath = Join-Path $OutDir "BestBudsWeightStation-Setup-v$Version.exe"
    if (-not (Test-Path $SetupPath)) {
        Write-Warning "Expected setup at $SetupPath was not found after ISCC."
        $SetupPath = $null
    } else {
        Write-Host "Wrote $SetupPath"
    }
} else {
    Write-Warning 'Inno Setup (ISCC.exe) not found. Zip package only. Install Inno Setup 6 to produce Setup.exe.'
}

$Receipt = [ordered]@{
    created_at           = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    version              = $Version
    platform             = 'windows-x64'
    code_signed          = $false
    physical_device_pass = $false
    python_used          = "$Python"
    pyinstaller_dir      = 'dist/BestBudsWeightStation'
    zip_path             = "dist/windows/$ZipName"
    setup_path           = if ($SetupPath) { "dist/windows/$(Split-Path $SetupPath -Leaf)" } else { $null }
    inno_available       = [bool]$Iscc
    non_claims           = @(
        'Not Authenticode-signed.',
        'Not legal-for-trade certification.',
        'No production metrology claim.'
    )
}
$ReceiptPath = Join-Path $OutDir "windows_build_receipt.v$Version.json"
$Receipt | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 $ReceiptPath
Write-Host "Wrote $ReceiptPath"
Write-Host 'Windows packaging completed.'
