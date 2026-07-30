# Windows Packaging

Windows 10/11 x64 is the primary PC operator target. Run `build_windows.ps1` on a native Windows host. The script installs the desktop and serial dependencies, runs tests, builds the PyInstaller artifact, and invokes `verify_windows.ps1`.

Source presence is not native runtime evidence. A successful Windows claim requires the build and verification scripts to execute on Windows and return receipts.
