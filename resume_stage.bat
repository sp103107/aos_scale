@echo off
setlocal
if "%~1"=="" (echo Usage: resume_stage.bat RUN_ID & exit /b 2)
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (py -3 scripts\launcher.py stage resume --run-id %1 --plan cursor_ready) else (python scripts\launcher.py stage resume --run-id %1 --plan cursor_ready)
exit /b %ERRORLEVEL%
