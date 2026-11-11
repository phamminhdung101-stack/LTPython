@echo off
title DocUni - Django REST Backend
echo ========================================================
echo DANG KHOI CHAY DOCUNI DJANGO BACKEND API
echo ========================================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Dang chay tai dia chi: http://127.0.0.1:8000/api/
echo.
venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
pause
