@echo off
setlocal EnableExtensions
title Kokoro Vietnamese TTS

cd /d "%~dp0"
if errorlevel 1 goto BAD_FOLDER

set "VENV_DIR=%CD%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

echo ==========================================
echo   KOKORO VIETNAMESE TTS
echo ==========================================
echo.

if exist "%VENV_PY%" goto CHECK_PYTHON

echo [1/3] Creating Python environment...
where py.exe >nul 2>nul
if errorlevel 1 goto TRY_PYTHON_EXE

py -3.11 -m venv "%VENV_DIR%" >nul 2>nul
if not errorlevel 1 goto CHECK_PYTHON
py -3 -m venv "%VENV_DIR%"
if errorlevel 1 goto FAILED
goto CHECK_PYTHON

:TRY_PYTHON_EXE
where python.exe >nul 2>nul
if errorlevel 1 goto NO_PYTHON
python.exe -m venv "%VENV_DIR%"
if errorlevel 1 goto FAILED

:CHECK_PYTHON
"%VENV_PY%" -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 goto OLD_PYTHON

if not exist "%VENV_DIR%\.kokoro-deps-v3" goto INSTALL_PACKAGES
"%VENV_PY%" -c "import huggingface_hub, numpy, onnxruntime, soundfile, torch, vig2p" >nul 2>nul
if not errorlevel 1 goto RUN_SERVER

:INSTALL_PACKAGES
echo [2/3] Installing Kokoro Vietnamese dependencies...
echo This can take several minutes on the first run.
echo Keep this window open.
echo.
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto FAILED
"%VENV_PY%" -m pip install -r "%CD%\requirements.txt"
if errorlevel 1 goto FAILED
"%VENV_PY%" -c "import huggingface_hub, numpy, onnxruntime, soundfile, torch, vig2p"
if errorlevel 1 goto FAILED
type nul > "%VENV_DIR%\.kokoro-deps-v3"

:RUN_SERVER
echo.
echo [3/3] Starting server...
echo Open: http://127.0.0.1:8000
echo Press Control+C in this window to stop.
echo.
start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"
"%VENV_PY%" "%CD%\server.py"
goto PAUSE_END

:NO_PYTHON
echo.
echo ERROR: Python was not found.
echo Install Python 3.11 64-bit from https://www.python.org/downloads/windows/
echo IMPORTANT: Select "Add Python to PATH" during installation.
goto PAUSE_END

:OLD_PYTHON
echo.
echo ERROR: Python 3.10 or newer is required.
echo Python 3.11 64-bit is recommended.
echo Delete the .venv folder after installing Python 3.11, then run this file again.
goto PAUSE_END

:BAD_FOLDER
echo.
echo ERROR: Cannot open the application folder.
echo Extract the ZIP completely before running this file.
goto PAUSE_END

:FAILED
echo.
echo ERROR: Installation or server startup failed.
echo Read the error above or send a photo of this window.

:PAUSE_END
echo.
pause
endlocal
