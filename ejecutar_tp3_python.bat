@echo off
chcp 65001 >nul
title UNViMe - Analisis y Diseno de Algoritmos - TP 3: Transforma y Conquista
cd /d "%~dp0"
if exist "C:\Users\julio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "C:\Users\julio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tp3_transforma_y_conquista.py
) else (
    python tp3_transforma_y_conquista.py
)
pause
