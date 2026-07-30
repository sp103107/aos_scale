@echo off
setlocal
if "%~1"=="" (echo Usage: run_stage.bat STAGE_ID & exit /b 2)
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (py -3 scripts\launcher.py stage run --stage %1 --run-id manual-stage) else (python scripts\launcher.py stage run --stage %1 --run-id manual-stage)
exit /b %ERRORLEVEL%
