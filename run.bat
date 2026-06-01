@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\" (
    echo [setup] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [error] Failed to create venv. Is Python installed and on PATH?
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo [setup] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [error] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    call .venv\Scripts\activate.bat
)

echo [run] Starting Browser Logger...
python browser_logger.py
if errorlevel 1 pause
endlocal
