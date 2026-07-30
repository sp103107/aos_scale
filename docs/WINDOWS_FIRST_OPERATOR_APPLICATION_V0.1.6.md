# Windows-First Operator Application — v0.1.6

Windows is the primary PC target. PySide6 is the primary operator interface. Linux uses the same application architecture, with Tk as a fallback when PySide6 is unavailable.

## Runtime layers

```text
PySide6 or Tk
→ OperatorRuntime
→ ApplicationController
→ CaptureMachine / ScaleControlService / DeviceService
→ SessionStore and Alice receipt gate
```

The frontend does not write authoritative records. The reading worker does not write authoritative records. Every sample and operator action enters through canonical controller actions.

## Windows data defaults

```text
%LOCALAPPDATA%\BestBudsWeightStation\
├── config
├── logs
├── runs
├── recovery
└── exports
```

Normal operation is designed not to require administrator privileges.

## Native evidence boundary

The `.bat`, PowerShell, PyInstaller, install, uninstall, and verify sources are implemented. Native Windows runtime remains `NOT_RUN` until those files execute successfully on a Windows 10/11 host and produce receipts.
