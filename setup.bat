@echo off
REM Setup script for FinOps GenAI Agent (Windows)
REM This script automates the virtual environment setup

echo ========================================
echo FinOps GenAI Agent - Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
if exist venv (
    echo [WARNING] Virtual environment already exists.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo [INFO] Removing old virtual environment...
        rmdir /s /q venv
    ) else (
        echo [INFO] Using existing virtual environment.
        goto :install
    )
)

echo [INFO] Creating virtual environment...
python -m venv venv
echo [OK] Virtual environment created!
echo.

:install
REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo [OK] Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Configure AWS credentials:
echo    aws configure
echo    OR
echo    copy .env.example .env  # and edit with your credentials
echo.
echo 3. Setup AWS infrastructure:
echo    python setup_aws.py
echo.
echo 4. Run the app:
echo    streamlit run streamlit_app.py
echo.
echo 5. Generate sample data (optional):
echo    python generate_sample_data.py
echo.
echo Documentation:
echo    - Quick Start: QUICKSTART.md
echo    - Virtual Env Guide: VIRTUAL_ENV_GUIDE.md
echo    - Full Docs: README_STREAMLIT.md
echo.

pause
