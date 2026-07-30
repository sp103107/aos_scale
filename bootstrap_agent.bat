@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 scripts\launcher.py bootstrap %*
) else (
  python scripts\launcher.py bootstrap %*
)
exit /b %ERRORLEVEL%
