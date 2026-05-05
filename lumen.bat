@echo off
REM Lumen CLI Tool - Execution script for Windows

REM Check if Python is available
where python3 >nul 2>&1
if %errorlevel% neq 0 (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH
        exit /b 1
    )
)

REM Check if the script is being run from the project directory
if not exist lumen.py (
    echo [ERROR] lumen.py not found. Please run this script from the project directory.
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo [INFO] Installing dependencies...
    REM Use pip from virtual environment if it exists, otherwise use system pip
    if exist venv\Scripts\pip (
        venv\Scripts\pip install -r requirements.txt
    ) else (
        pip install -r requirements.txt
    )
)

REM Run the Python script with the provided arguments
REM Use virtual environment Python if it exists
if exist venv\Scripts\python (
    venv\Scripts\python lumen.py %*
) else (
    python lumen.py %*
)