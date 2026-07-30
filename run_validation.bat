@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 scripts\launcher.py validation %*
) else (
  python scripts\launcher.py validation %*
)
exit /b %ERRORLEVEL%
