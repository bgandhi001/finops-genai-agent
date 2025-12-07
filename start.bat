@echo off
REM Quick start script for FinOps GenAI Agent (Windows)

echo ========================================
echo Starting FinOps GenAI Agent
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Run: python -m venv venv
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found
    echo Copy .env.example to .env and add your AWS credentials
    echo.
)

REM Start the app
echo [INFO] Starting Streamlit app...
echo [INFO] Opening http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

streamlit run streamlit_app.py
