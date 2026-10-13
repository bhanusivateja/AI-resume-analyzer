@echo off
title AI Resume Analyzer - Intelligent ATS & Career Assistant
echo =====================================================================
echo           Starting AI Resume Analyzer Application...
echo =====================================================================
echo.

cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH.
    echo Please install Python 3.10+ from https://python.org and ensure "Add Python to PATH" is checked.
    pause
    exit /b
)

:: Install/Verify dependencies if requirements.txt exists
echo Checking Python dependencies...
python -c "import streamlit, sklearn, pdfminer, reportlab, plotly" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing missing requirements from requirements.txt...
    pip install -r requirements.txt
)

:: Launch Streamlit app
echo.
echo Launching web application on http://localhost:8501 ...
echo Press Ctrl+C in this window to stop the server.
echo.

start "" http://localhost:8501
streamlit run app.py --server.port 8501
