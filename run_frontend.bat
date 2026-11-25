@echo off
title DocUni - Reflex Frontend
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================================
echo   DOCUNI - KHO TAI LIEU VA AI TIM KIEM NGU CANH
echo   DANG KHOI CHAY REFLEX FRONTEND
echo ========================================================
cd /d "%~dp0frontend_app"

if not exist "..\venv\Scripts\activate.bat" (
    echo [LOI] Khong tim thay moi truong ao virtualenv tai ..\venv\Scripts\activate.bat
    echo Vui long kiem tra lai thu muc virtual environment.
    pause
    exit /b 1
)

call ..\venv\Scripts\activate.bat

echo [1/3] Kiem tra phien ban Python va Reflex:
..\venv\Scripts\python.exe -c "import sys, reflex; print(f'  • Python: {sys.version.split()[0]}'); print(f'  • Reflex: {reflex.__version__}')"

echo [2/3] Dia chi dich vu:
echo   • Frontend UI:       http://localhost:3000
echo   • Reflex Event Port: http://localhost:8001
echo   • Django Backend:    http://localhost:8000
echo.
echo [3/3] Dang khoi chay tien trinh Reflex...
..\venv\Scripts\python.exe -m reflex run --backend-port 8001

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo [CANH BAO] Reflex Frontend da dung voi ma loi %ERRORLEVEL%.
    echo ========================================================
)
pause
