@echo off
chcp 65001 > nul
title Telegram Video Hub Setup
echo ======================================================
echo    TELEGRAM VIDEO HUB - WIZARD KET NOI TELEGRAM BOT
echo ======================================================
echo.
cd /d "%~dp0\.."
python -m telegram_video_hub.cli setup
echo.
pause
