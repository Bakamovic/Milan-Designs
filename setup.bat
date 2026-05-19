@echo off
cd /d "%~dp0"
echo.
echo  First time? Run: python install.py
echo  That creates a Desktop launcher so you never need this window again.
echo.
echo  Milan Designs - Setup ^& Launch
echo  ================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed.
    echo  Download it from: https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist yet
if not exist "venv\" (
    echo  Creating virtual environment...
    python -m venv venv
    echo  Done.
    echo.
)

:: Activate and install dependencies
echo  Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet
echo  Done.
echo.

:: If secrets file is missing, copy the example and stop so the user fills it in
if not exist ".streamlit\secrets.toml" (
    echo  First-time setup: secrets file not found.
    echo  Copying template to .streamlit\secrets.toml ...
    copy ".streamlit\secrets.toml.example" ".streamlit\secrets.toml" >nul
    echo.
    echo  ACTION REQUIRED:
    echo  Open .streamlit\secrets.toml and replace "change_me" with real passwords.
    echo  Then run setup.bat again to launch the app.
    echo.
    start notepad ".streamlit\secrets.toml"
    pause
    exit /b 0
)

:: Launch the app
echo  Starting app...
echo  Press Ctrl+C here to stop the app.
echo.
start /b powershell -WindowStyle Hidden -Command "Start-Sleep 6; Start-Process 'http://localhost:8501'"
streamlit run app.py
