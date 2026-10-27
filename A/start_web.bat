@echo off
chcp 65001 >nul
title VibeRadar - Web Dashboard
cd /d "%~dp0"
echo ========================================================
echo   🌌 VIBERADAR — KHOI DONG WEB DASHBOARD
echo   Mo trinh duyet tai: http://127.0.0.1:8765
echo ========================================================
echo.
python run_web.py
pause
