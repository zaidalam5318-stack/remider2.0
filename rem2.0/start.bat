@echo off
REM Professional Reminder App - Windows Launcher

color 0A
cls
title Reminder Pro - Starting...

echo.
echo   ╔══════════════════════════════════════╗
echo   ║   PROFESSIONAL REMINDER APP v1.0     ║
echo   ║   Starting Services...               ║
echo   ╚══════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not installed. Please install Python 3.7+
    echo Visit: https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
cd backend
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [✓] Dependencies installed

echo [2/3] Starting backend server...
start "Reminder Pro - Backend" python app.py
timeout /t 3 /nobreak >nul

echo [3/3] Opening app in browser...
timeout /t 1 /nobreak >nul
start http://localhost:3000

cls
echo.
echo   ╔══════════════════════════════════════╗
echo   ║   REMINDER PRO - RUNNING             ║
echo   ╠══════════════════════════════════════╣
echo   ║ App: http://localhost:3000          ║
echo   ╚══════════════════════════════════════╝
echo.
echo   [✓] App is ready in your browser
echo   [!] Keep this window open to run the app
echo   [!] Close all windows to stop the app
echo.
pause
