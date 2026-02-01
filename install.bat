@echo off
echo ==========================================
echo KunUz Parser - Quick Start
echo ==========================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

:: Установка зависимостей
echo [1/2] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/2] Installing Playwright browser...
playwright install chromium

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo Try: python examples.py
echo.
pause
