#!/bin/bash

echo "========================================"
echo "POSH Video Generation System"
echo "========================================"
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please install Anaconda or Miniconda."
    exit 1
fi

# Activate POSH environment
echo "Activating POSH conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate POSH

if [ $? -ne 0 ]; then
    echo "Error: Could not activate POSH environment."
    echo "Please create it with: conda create -n POSH python=3.9"
    exit 1
fi

# Run the application
echo "Starting POSH Video Generation System..."
echo
python main.py
