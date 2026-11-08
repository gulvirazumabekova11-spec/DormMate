@echo off
setlocal
cd /d "%~dp0"
set "API_URL=http://localhost:8000"
title DormMate Launcher

echo ======================================
echo   DormMate - Starting
 echo ======================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python 3.11 or newer was not found. Install Python first.
        pause
        exit /b 1
    )
)

echo Installing/checking dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Could not install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo Preparing sample database...
.venv\Scripts\python.exe -m app.database.seed
if errorlevel 1 (
    echo ERROR: Could not prepare the database.
    pause
    exit /b 1
)

start "DormMate API" cmd /k "cd /d ""%~dp0"" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload"
timeout /t 3 /nobreak >nul
start "DormMate UI" cmd /k "cd /d ""%~dp0"" && .venv\Scripts\python.exe -m streamlit run app/frontend/ui.py"
timeout /t 3 /nobreak >nul
start "" "http://localhost:8501"

echo.
echo DormMate is running. Close the server windows to stop it.
endlocal



