@echo off
echo ========================================
echo POSH Video Generation System
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Conda not found. Please install Anaconda or Miniconda.
    pause
    exit /b 1
)

REM Activate POSH environment
echo Activating POSH conda environment...
call conda activate POSH
if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not activate POSH environment.
    echo Please create it with: conda create -n POSH python=3.9
    pause
    exit /b 1
)

REM Run the application
echo Starting POSH Video Generation System...
echo.
python main.py

pause
