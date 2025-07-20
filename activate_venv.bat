@echo off
REM Simple script to activate the virtual environment on Windows

if exist "venv" (
    echo 🚀 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated!
    echo 📁 Current Python: %VIRTUAL_ENV%\Scripts\python.exe
    echo 📦 Current pip: %VIRTUAL_ENV%\Scripts\pip.exe
    echo.
    echo 💡 To deactivate, run: deactivate
    echo 💡 To run the app: uvicorn app.main:app --reload
) else (
    echo ❌ Virtual environment not found!
    echo 💡 Run 'setup_venv.bat' to create and setup the virtual environment.
) 