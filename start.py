import os
import sys
import subprocess
import shutil
import socket
import threading
import webbrowser

# Always run from the directory this file lives in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print()
print(" Milan Designs - Setup & Launch")
print(" ================================")
print()

# Python version check
if sys.version_info < (3, 8):
    print(" ERROR: Python 3.8 or later is required.")
    print(f" You have Python {sys.version_info.major}.{sys.version_info.minor}.")
    print(" Download the latest version from: https://www.python.org/downloads/")
    input(" Press Enter to close...")
    sys.exit(1)

# Create virtual environment if missing
venv_dir = "venv"
if sys.platform == "win32":
    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    venv_pip    = os.path.join(venv_dir, "Scripts", "pip.exe")
else:
    venv_python = os.path.join(venv_dir, "bin", "python3")
    venv_pip    = os.path.join(venv_dir, "bin", "pip")

if not os.path.isdir(venv_dir):
    print(" Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    print(" Done.")
    print()

# Install dependencies
print(" Installing dependencies...")
subprocess.run([venv_pip, "install", "-r", "requirements.txt", "-q"], check=True)
print(" Done.")
print()

# Handle secrets file
secrets_path  = os.path.join(".streamlit", "secrets.toml")
example_path  = os.path.join(".streamlit", "secrets.toml.example")

if not os.path.isfile(secrets_path):
    print(" First-time setup: secrets file not found.")
    print(" Copying template...")
    shutil.copy(example_path, secrets_path)
    print()
    print(" ACTION REQUIRED:")
    print(" Open .streamlit/secrets.toml and replace 'change_me' with real passwords.")
    print(" Then run start.py again to launch the app.")
    print()
    if sys.platform == "win32":
        os.startfile(secrets_path)
    else:
        subprocess.run(["open", "-e", secrets_path])
    input(" Press Enter to close...")
    sys.exit(0)

# Open browser once Streamlit is ready
def open_browser():
    while True:
        try:
            s = socket.create_connection(("localhost", 8501), timeout=1)
            s.close()
            webbrowser.open("http://localhost:8501")
            break
        except OSError:
            import time
            time.sleep(1)

threading.Thread(target=open_browser, daemon=True).start()

# Launch the app
print(" Starting app...")
print(" Press Ctrl+C to stop.")
print()
subprocess.run([venv_python, "-m", "streamlit", "run", "app.py"])
