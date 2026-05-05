#!/bin/bash
# Lumen CLI Tool - Execution script for Linux/macOS

# Check if Python is available
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 is not installed or not in PATH"
    exit 1
fi

# Check if the script is being run from the project directory
if [ ! -f "lumen.py" ]; then
    echo "[ERROR] lumen.py not found. Please run this script from the project directory."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies..."
    # Use pip from virtual environment if it exists, otherwise use system pip
    if [ -f "venv/bin/pip" ]; then
        venv/bin/pip install -r requirements.txt
    else
        pip3 install -r requirements.txt
    fi
fi

# Run the Python script with the provided arguments
# Use virtual environment Python if it exists
if [ -f "venv/bin/python3" ]; then
    venv/bin/python3 lumen.py "$@"
else
    python3 lumen.py "$@"
fi