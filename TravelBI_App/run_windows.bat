@echo off
cd /d "%~dp0"
if not exist .venv (
    echo Creation de l environnement Python...
    python -m venv .venv
    call .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)
python app.py
