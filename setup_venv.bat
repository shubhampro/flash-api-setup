@echo off
REM FastAPI Multi-Database Project Virtual Environment Setup Script for Windows
REM This script creates and activates a virtual environment for the project

setlocal enabledelayedexpansion

echo 🚀 FastAPI Multi-Database Project Setup
echo ======================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.8+ first.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Found Python %PYTHON_VERSION%

REM Check if pip is installed
echo [INFO] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed. Please install pip first.
    pause
    exit /b 1
)
echo [SUCCESS] Found pip

REM Create virtual environment
if exist "venv" (
    echo [WARNING] Virtual environment 'venv' already exists.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo [INFO] Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo [INFO] Using existing virtual environment.
        goto :activate_venv
    )
)

echo [INFO] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created successfully!

:activate_venv
REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify activation
if "%VIRTUAL_ENV%"=="" (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated!
echo [INFO] Python path: %VIRTUAL_ENV%\Scripts\python.exe
echo [INFO] Pip path: %VIRTUAL_ENV%\Scripts\pip.exe

REM Install dependencies
echo [INFO] Installing project dependencies...

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install requirements
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully!
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    if exist "env.example" (
        copy env.example .env >nul
        echo [SUCCESS] .env file created from env.example
        echo [WARNING] Please edit .env file with your MySQL database credentials!
    ) else (
        echo [WARNING] env.example not found. Please create .env file manually.
    )
) else (
    echo [INFO] .env file already exists.
)

REM Display next steps
echo.
echo ==========================================
echo [SUCCESS] Virtual environment setup completed!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your MySQL credentials:
echo    notepad .env
echo.
echo 2. Set up MySQL databases:
echo    mysql -u root -p
echo    CREATE DATABASE mono_api_main;
echo    CREATE DATABASE mono_api_analytics;
echo    CREATE DATABASE mono_api_logs;
echo.
echo 3. Initialize databases:
echo    python -m app.db.init_db
echo.
echo 4. Test database connections:
echo    python test_connections.py
echo.
echo 5. Run the application:
echo    uvicorn app.main:app --reload
echo.
echo 6. Access the API documentation:
echo    http://localhost:8000/api/v1/docs
echo.
echo [WARNING] Remember to activate the virtual environment in new command prompts:
echo    venv\Scripts\activate.bat
echo.

pause 