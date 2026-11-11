@echo off
title DocUni - Khoi Chay Toan Bo He Thong
echo ========================================================
echo DANG KHOI CHAY DOCUNI (BACKEND DJANGO + FRONTEND REFLEX)
echo ========================================================
echo.
echo 1. Dang mo cua so Django Backend API (port 8000)...
start "DocUni Django Backend" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && python backend\manage.py runserver 127.0.0.1:8000"

timeout /t 3 /nobreak >nul

echo 2. Dang mo cua so Reflex Frontend (port 3000)...
start "DocUni Reflex Frontend" cmd /k "cd /d "%~dp0frontend_app" && call ..\venv\Scripts\activate.bat && reflex run"

echo.
echo ========================================================
echo HE THONG DANG CHAY:
echo - Backend API:  http://127.0.0.1:8000/api/
echo - Frontend Web: http://localhost:3000
echo.
echo LUU Y: Vui long giu ca 2 cua so Backend va Frontend mo!
echo ========================================================
echo Nhan phim bat ky de dong cua so khoi dong nay.
pause >nul
