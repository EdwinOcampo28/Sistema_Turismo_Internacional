@echo off
chcp 65001 >nul
cd /d "%~dp0"
python turismo.py
if errorlevel 1 (echo. & echo No se pudo iniciar. Verifica que Python este instalado.)
pause
