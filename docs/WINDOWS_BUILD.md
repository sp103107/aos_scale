# Windows Build - v2.0.0-rc2

Windows 10/11 x64 is the primary operator target. See [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) for hardware and OS requirements.

## Build on a native Windows host

Requirements on the build PC:

- Python 3.11 or 3.12
- PowerShell
- Optional but recommended: [Inno Setup 6](https://jrsoftware.org/isinfo.php) (`ISCC.exe` on `PATH` or under Program Files) to produce `BestBudsWeightStation-Setup-v*.exe`

```powershell
.\packaging\windows\build_windows.ps1
```

The script:

1. Installs desktop/serial/dev deps and PyInstaller
2. Runs pytest
3. Soft-runs launcher validators (warn-first)
4. Builds the PyInstaller onedir app
5. Runs `verify_windows.ps1` (`--version` and simulator self-test)
6. Zips `dist\windows\BestBudsWeightStation-windows-x64-v{VERSION}.zip`
7. If Inno Setup is available, compiles `BestBudsWeightStation-Setup-v{VERSION}.exe`
8. Writes `dist\windows\windows_build_receipt.v{VERSION}.json`

## Install without the Setup EXE

```powershell
.\packaging\windows\install_windows.ps1
.\packaging\windows\uninstall_windows.ps1
```

Install root: `%LOCALAPPDATA%\BestBudsWeightStation\app`  
Run data: `%LOCALAPPDATA%\BestBudsWeightStation\runs` (preserved on uninstall)

## Claims

Source presence, PowerShell syntax checks, and Linux-side validation are **not** a native Windows runtime pass. A successful Windows packaging claim requires this build and verification to execute on Windows and produce the receipt. Builds are **not Authenticode-signed** in this pass. No legal-for-trade claim.
