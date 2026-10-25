@echo off
REM Start the PlantIQ backend on this laptop. Phones on the same Wi-Fi connect to the "Phone:" address it prints.
REM First run: creates backend\.venv, installs dependencies, builds the web UI and prepares the RAG models.
setlocal
if "%PORT%"=="" set PORT=8000
cd /d "%~dp0..\backend"
if not exist .venv\Scripts\python.exe (
  echo [setup] creating Python 3.11 virtual environment...
  py -3.11 -m venv .venv || goto :error
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements.txt || goto :error
)
if not exist .env (
  copy .env.example .env >nul
  echo [setup] created backend\.env from .env.example - add your GEMINI_API_KEY / GROQ_API_KEY there.
)
if not exist static\index.html (
  echo [setup] building the web UI...
  .venv\Scripts\python.exe ..\scripts\sync_web.py || echo [warn] web UI not built - API still works.
)
.venv\Scripts\python.exe scripts\prepare_models.py
.venv\Scripts\python.exe run.py --port %PORT% --warm %*
goto :eof
:error
echo Setup failed. See the messages above.
exit /b 1
