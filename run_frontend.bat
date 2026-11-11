@echo off
title DocUni - Reflex Frontend
echo ========================================================
echo DANG KHOI CHAY DOCUNI REFLEX FRONTEND
echo ========================================================
cd /d "%~dp0frontend_app"
call ..\venv\Scripts\activate.bat
echo Dang chay tai dia chi: http://localhost:3000
echo.
..\venv\Scripts\reflex.exe run
pause
