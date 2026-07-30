# Windows Packaging

Windows 10/11 x64 is the primary PC operator target. See [docs/SYSTEM_REQUIREMENTS.md](../../docs/SYSTEM_REQUIREMENTS.md) and [docs/WINDOWS_BUILD.md](../../docs/WINDOWS_BUILD.md).

## Quick build

```powershell
.\packaging\windows\build_windows.ps1
```

Produces:

- `dist\BestBudsWeightStation\` — PyInstaller onedir app
- `dist\windows\BestBudsWeightStation-windows-x64-v{VERSION}.zip`
- `dist\windows\BestBudsWeightStation-Setup-v{VERSION}.exe` when Inno Setup 6 is installed
- `dist\windows\windows_build_receipt.v{VERSION}.json`

## Zip install / uninstall

```powershell
.\packaging\windows\install_windows.ps1
.\packaging\windows\uninstall_windows.ps1
```

Source presence is not native runtime evidence. A successful Windows packaging claim requires the build and verification scripts to execute on Windows and return the receipt. Builds are not Authenticode-signed in this pass.
