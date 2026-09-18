@echo off
echo =======================================================
echo   Starting Admission Counselling Frontend (React + Vite)
echo =======================================================
cd /d "%~dp0frontend"
set "PATH=%~dp0tools\node;%PATH%"
call "%~dp0tools\node\npm.cmd" run dev
pause
