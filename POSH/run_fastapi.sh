#!/bin/bash

echo "========================================"
echo "POSH Video Generation System - FastAPI"
echo "========================================"
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Warning: Conda not found. Using system Python."
    python run_fastapi.py
    exit 0
fi

# Try to activate POSH environment
echo "Activating POSH conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate POSH 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Warning: Could not activate POSH environment. Using current environment."
fi

# Run the FastAPI launcher
echo "Starting FastAPI interface..."
echo
python run_fastapi.py

