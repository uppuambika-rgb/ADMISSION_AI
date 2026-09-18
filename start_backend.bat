@echo off
echo =======================================================
echo   Starting Admission Counselling Backend (FastAPI)
echo =======================================================
cd /d "%~dp0"
call .\backend\venv\Scripts\python.exe .\backend\run.py
pause
