# Milan Designs — Mac Setup Guide

This guide walks you through setting up the Milan Designs Shop Management App on a Mac from scratch.

---

## Prerequisites

Download and install Python 3.12 from [python.org](https://www.python.org/downloads/).

Verify the installation by opening Terminal and running:

```bash
python3 --version
```

It should print `Python 3.12.x`.

---

## Step 1 — Download the Project

1. Go to [github.com/Bakamovic/Milan-Designs](https://github.com/Bakamovic/Milan-Designs)
2. Click the green **Code** button
3. Click **Download ZIP**
4. Unzip the downloaded file to your Desktop

You should now have a folder called `Milan-Designs-master` on your Desktop.

---

## Step 2 — Copy the Database

Copy the `shop_app.db` file from the Windows machine into the `Milan-Designs-master` folder on the Desktop.

> **Important:** If this file is missing the app will crash on startup with no visible error message.

---

## Step 3 — Fix the Altair Dependency

There is a known issue where `altair==6.1.0` does not exist as a stable release on Mac. Run this command in Terminal to fix it:

```bash
sed -i '' 's/altair==6.1.0/altair>=6.0.0/' ~/Desktop/Milan-Designs-master/requirements.txt
```

> This is a one-time fix. You only need to do this once.

---

## Step 4 — Run the Installer

```bash
python3 ~/Desktop/Milan-Designs-master/install.py
```

This will:
- Create a virtual environment
- Install all required packages
- Open `.streamlit/secrets.toml` automatically

When the file opens, fill in the real passwords and save it.

---

## Step 5 — Run the Installer Again

After filling in the passwords, run the installer a second time:

```bash
python3 ~/Desktop/Milan-Designs-master/install.py
```

This creates a Milan Designs launcher on the Desktop.

---

## Step 6 — Launch the App

The Desktop launcher does not work reliably yet. Use this Terminal command instead:

```bash
cd ~/Desktop/Milan-Designs-master && source venv/bin/activate && python -m streamlit run app.py
```

Then open your browser and go to:

```
http://localhost:8501
```

---

## Important Notes

- The app runs as long as the Terminal window stays open. **Do not close Terminal** while using the app — closing it stops the app.
- The `shop_app.db` file must be inside the `Milan-Designs-master` folder at all times.
- Step 3 is a Mac-only workaround. Windows users do not need it.
- Step 5 and 6 will be improved in a future update to make the Desktop launcher reliable.

---

## Stopping the App

Go to the Terminal window and press **Ctrl + C**.
