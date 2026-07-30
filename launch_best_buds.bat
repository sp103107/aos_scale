@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 scripts\launcher.py launch %*
) else (
  python scripts\launcher.py launch %*
)
exit /b %ERRORLEVEL%
