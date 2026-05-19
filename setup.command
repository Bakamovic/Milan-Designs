#!/bin/bash
cd "$(dirname "$0")"

echo ""
echo " Milan Designs - Setup & Launch"
echo " ================================"
echo ""

# Check Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo " ERROR: Python 3 is not installed."
    echo " Download it from: https://www.python.org/downloads/"
    echo " Or install via Homebrew: brew install python"
    echo ""
    read -p " Press Enter to close..."
    exit 1
fi

# Create virtual environment if it doesn't exist yet
if [ ! -d "venv" ]; then
    echo " Creating virtual environment..."
    python3 -m venv venv
    echo " Done."
    echo ""
fi

# Activate and install dependencies
echo " Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet
echo " Done."
echo ""

# If secrets file is missing, copy the example and stop so the user fills it in
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo " First-time setup: secrets file not found."
    echo " Copying template to .streamlit/secrets.toml ..."
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo ""
    echo " ACTION REQUIRED:"
    echo " Open .streamlit/secrets.toml and replace 'change_me' with real passwords."
    echo " Then double-click setup.command again to launch the app."
    echo ""
    open -e .streamlit/secrets.toml 2>/dev/null || open .streamlit/secrets.toml
    read -p " Press Enter to close..."
    exit 0
fi

# Launch the app
echo " Starting app..."
echo " Press Ctrl+C here to stop the app."
echo ""
(while ! nc -z localhost 8501 2>/dev/null; do sleep 1; done && open "http://localhost:8501") &
streamlit run app.py
