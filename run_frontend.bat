@echo off
title DocUni - Reflex Frontend
echo ========================================================
echo DANG KHOI CHAY DOCUNI REFLEX FRONTEND
echo ========================================================
cd /d "%~dp0frontend_app"
call ..\venv\Scripts\activate.bat
echo Dang chay Frontend: http://localhost:3000
echo Backend Reflex Event: http://localhost:8001 (khong anh huong den Django 8000)
echo.
..\venv\Scripts\reflex.exe run --backend-port 8001
pause
