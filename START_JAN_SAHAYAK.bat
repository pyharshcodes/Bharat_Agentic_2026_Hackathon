@echo off
title Jan-Sahayak AI - 1-Click Launcher (Team Bits and Bytes)
color 0A

echo ======================================================================
echo    JAN-SAHAYAK AI (जन-सहायक AI)
echo    Autonomous Welfare & Civic Rights Action Agent for Bharat
echo    Team: Bits and Bytes (Harsh Deep Chak & Pallak Devi)
echo ======================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python aapke PC me installed nahi hai ya PATH me add nahi hai!
    echo Kripya https://www.python.org/downloads/ se Python download karein.
    echo (Install karte waqt 'Add Python to PATH' par zaroor tick lagayein).
    echo.
    pause
    exit /b
)

echo [1/3] Python verified successfully...

:: 2. Install / Verify Requirements
echo [2/3] Checking & Installing dependencies (fastapi, uvicorn, reportlab, etc.)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Dependencies install me dikkat aayi, standard pip run kar rahe hain...
    pip install -r requirements.txt
)

:: 3. Launch Browser and Server
echo [3/3] Starting Production Server on http://127.0.0.1:8000 ...
echo.
echo Browser 2 second me auto-open hoga: http://127.0.0.1:8000
echo Server ko stop karne ke liye is window me 'Ctrl + C' dabayein.
echo.

start "" http://127.0.0.1:8000
python server.py

pause
