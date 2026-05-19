import os
import sys
import subprocess
import shutil
import stat

# Always run from the directory this file lives in
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

print()
print(" Milan Designs - First-Time Setup")
print(" ==================================")
print()

# Python version check
if sys.version_info < (3, 8):
    print(" ERROR: Python 3.8 or later is required.")
    print(f" You have Python {sys.version_info.major}.{sys.version_info.minor}.")
    print(" Download from: https://www.python.org/downloads/")
    input(" Press Enter to close...")
    sys.exit(1)

# Venv paths
venv_dir = "venv"
if sys.platform == "win32":
    venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
else:
    venv_pip = os.path.join(venv_dir, "bin", "pip")

# Create virtual environment if missing
if not os.path.isdir(venv_dir):
    print(" Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    print(" Done.")
    print()

# Install dependencies
print(" Installing dependencies (this may take a minute)...")
subprocess.run([venv_pip, "install", "-r", "requirements.txt", "-q"], check=True)
print(" Done.")
print()

# Handle secrets file
secrets_path = os.path.join(".streamlit", "secrets.toml")
example_path = os.path.join(".streamlit", "secrets.toml.example")

if not os.path.isfile(secrets_path):
    print(" Copying secrets template...")
    shutil.copy(example_path, secrets_path)
    print()
    print(" ACTION REQUIRED:")
    print(f" Open {secrets_path} and replace 'change_me' with real passwords.")
    print(" Then run install.py again to finish setup.")
    print()
    if sys.platform == "win32":
        os.startfile(secrets_path)
    else:
        subprocess.run(["open", "-e", secrets_path])
    input(" Press Enter to close...")
    sys.exit(0)

# Create Desktop launcher
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

if sys.platform == "win32":
    launcher_path = os.path.join(desktop, "Milan Designs.bat")
    launcher_content = (
        "@echo off\n"
        f'cd /d "{PROJECT_DIR}"\n'
        "call venv\\Scripts\\activate\n"
        'start /b powershell -WindowStyle Hidden -Command "Start-Sleep 5; Start-Process \'http://localhost:8501\'"\n'
        "streamlit run app.py\n"
    )
    with open(launcher_path, "w", newline="\n") as f:
        f.write(launcher_content)

else:
    launcher_path = os.path.join(desktop, "Milan Designs.command")
    launcher_content = (
        "#!/bin/bash\n"
        f'cd "{PROJECT_DIR}"\n'
        "source venv/bin/activate\n"
        "python -m streamlit run app.py &\n"
        "APP_PID=$!\n"
        "until nc -z localhost 8501 2>/dev/null; do sleep 1; done\n"
        "open http://localhost:8501\n"
        "wait $APP_PID\n"
    )
    # Force LF endings — critical for bash on Mac
    with open(launcher_path, "w", newline="\n") as f:
        f.write(launcher_content)
    # Make executable
    os.chmod(launcher_path, os.stat(launcher_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

print(" Setup complete.")
print()
print(f' Launcher created: {launcher_path}')
print()
print(' Double-click "Milan Designs" on your Desktop to start the app.')
print()
input(" Press Enter to close...")
