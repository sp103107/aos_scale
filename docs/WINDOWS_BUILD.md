# Windows Build - v0.1.9

Windows 10/11 x64 is the primary operator target. Run `packaging/windows/build_windows.ps1` on a native Windows host with Python 3.11 or 3.12. Validate with `packaging/windows/verify_windows.ps1`.

The Windows application uses PySide6 and `pyserial`. Source presence, PowerShell syntax, and Linux-side PyInstaller configuration validation are not native Windows runtime proof. No Windows-native pass is claimed in this bump.
