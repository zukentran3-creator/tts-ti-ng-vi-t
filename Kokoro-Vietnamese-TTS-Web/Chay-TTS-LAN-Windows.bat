@echo off
setlocal EnableExtensions
title Kokoro Vietnamese TTS - LAN

cd /d "%~dp0"
if errorlevel 1 goto BAD_FOLDER

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
if not exist "%VENV_PY%" goto NOT_INSTALLED

echo ==========================================
echo   KOKORO VIETNAMESE TTS - LAN MODE
echo ==========================================
echo.
echo Open http://YOUR-PC-IP:8000 on another device.
echo Both devices must use the same private Wi-Fi network.
echo Press Control+C to stop the server.
echo.
"%VENV_PY%" "%CD%\server.py" --host 0.0.0.0
goto PAUSE_END

:NOT_INSTALLED
echo.
echo ERROR: The Python environment does not exist.
echo Run Chay-TTS-Windows.bat first and wait for installation to finish.
goto PAUSE_END

:BAD_FOLDER
echo.
echo ERROR: Cannot open the application folder.
echo Extract the ZIP completely before running this file.

:PAUSE_END
echo.
pause
endlocal
