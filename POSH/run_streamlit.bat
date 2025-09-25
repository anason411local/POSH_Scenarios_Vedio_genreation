@echo off
echo ========================================
echo POSH Video Generation System - Web UI
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Conda not found. Using system Python.
    python run_streamlit.py
    pause
    exit /b 0
)

REM Try to activate POSH environment
echo Activating POSH conda environment...
call conda activate POSH 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not activate POSH environment. Using current environment.
)

REM Run the Streamlit launcher
echo Starting Streamlit interface...
echo.
python run_streamlit.py

pause
