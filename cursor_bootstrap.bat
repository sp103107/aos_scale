@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (py -3 scripts\launcher.py stage run-plan --plan cursor_ready --run-id cursor-ready-v0.1.7 %*) else (python scripts\launcher.py stage run-plan --plan cursor_ready --run-id cursor-ready-v0.1.7 %*)
exit /b %ERRORLEVEL%
