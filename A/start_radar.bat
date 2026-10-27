@echo off
chcp 65001 >nul
title VibeRadar - Trending & Idea Scanner
cd /d "%~dp0"
echo ========================================================
echo   🌌 VIBERADAR — QUET XU HUONG & NAY Y TUONG BAT CHOT
echo ========================================================
echo.
python run_radar.py
echo.
echo Nhan phim bat ky de thoat...
pause >nul
