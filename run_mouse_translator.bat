@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

if not defined PYTHON_EXE (
  python --version >nul 2>&1
  if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
  py -3 --version >nul 2>&1
  if not errorlevel 1 set "PYTHON_EXE=py -3"
)

if not defined PYTHON_EXE (
  echo Python 3.10+ was not found. Please install Python or create .venv first.
  pause
  exit /b 1
)

%PYTHON_EXE% main.py
endlocal
