@echo off
title PlantIQ - Dual CNN Model Comparator & Benchmark Suite
color 0A

echo =================================================================
echo   PlantIQ Dual CNN Model Comparator ^& Benchmark Suite
echo =================================================================
echo.
echo [*] Launching Model Comparator Web App...
echo.

if exist venv\Scripts\python.exe (
    echo [*] Using local virtual environment (venv)...
    venv\Scripts\python.exe run_app.py
) else if exist .venv\Scripts\python.exe (
    echo [*] Using local virtual environment (.venv)...
    .venv\Scripts\python.exe run_app.py
) else (
    echo [*] Using system python...
    python run_app.py
)

pause
