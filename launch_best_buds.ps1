$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 scripts/launcher.py launch @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python scripts/launcher.py launch @args
} else {
    throw 'Python 3.11 or 3.12 is required.'
}
exit $LASTEXITCODE
