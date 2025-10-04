@echo off
echo ========================================
echo POSH Video Generation System - FastAPI
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Conda not found. Using system Python.
    python run_fastapi.py
    pause
    exit /b 0
)

REM Try to activate POSH environment
echo Activating POSH conda environment...
call conda activate POSH 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not activate POSH environment. Using current environment.
)

REM Run the FastAPI launcher
echo Starting FastAPI interface...
echo.
python run_fastapi.py

pause

