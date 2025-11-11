@echo off
setlocal

REM ========= CONFIG =========
set "WORKDIR=C:\Users\Shai-Hulud\Downloads"
set "LOG=%WORKDIR%\logs"
set "SCRIPT=ingest_nba.py"

REM 1) Python del venv si existe; si no, Python global
set "PY=%WORKDIR%\.venv\Scripts\python.exe"
set "FALLBACK_PY=C:\Users\Shai-Hulud\AppData\Local\Programs\Python\Python313\python.exe"

REM 2) Credenciales GCP (service account JSON)
set "GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Shai-Hulud\Downloads\nba-ingest.json"

REM ========= PREP =========
if not exist "%LOG%" mkdir "%LOG%"
chcp 65001 >NUL
set PYTHONIOENCODING=utf-8

set "RUNPY=%PY%"
if not exist "%RUNPY%" set "RUNPY=%FALLBACK_PY%"

pushd "%WORKDIR%"

REM ========= LOG ROTATION BY TIMESTAMP =========
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set "TODAY=%%d-%%b-%%c"
set "NOW=%time: =0%"
set "NOW=%NOW::=-%"
set "OUTLOG=%LOG%\ingest_%date:~-4%%date:~3,2%%date:~0,2%_%NOW%.log"

echo [%date% %time%] Starting ingest with "%RUNPY%" > "%OUTLOG%" 2>&1

"%RUNPY%" "%SCRIPT%" >> "%OUTLOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"

echo [%date% %time%] Exit code: %EXITCODE% >> "%OUTLOG%" 2>&1

popd
endlocal
exit /b %EXITCODE%
