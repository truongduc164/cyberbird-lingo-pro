@echo off
chcp 65001 >nul
title VibeToApk Studio
cd /d "%~dp0"

echo ========================================================
echo    VibeToApk Studio - Web-to-APK Vibe Coding Studio
echo ========================================================
echo.
echo Dang khoi dong trinh gia lap va dong goi mobile app...
echo.

start "" "http://localhost:8888/web_studio/index.html"
python -m http.server 8888

pause
