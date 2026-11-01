@echo off
echo ========================================================
echo Running Backend Pytest Test Suite
echo ========================================================
cd /d "%~dp0\..\backend"
call "..\venv\Scripts\activate.bat"
pytest tests -v
