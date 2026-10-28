@echo off
chcp 65001 >nul
title CyberBird Lingo PRO v3.2 - AI Curator & Cloud OTA (DEAN OPTIMIZE)
cd /d "%~dp0"

echo ====================================================================
echo   CYBERBIRD LINGO PRO v3.2 - AI PEDAGOGICAL CURATOR ^& CLOUD OTA 24/7
echo ====================================================================

echo [1/2] Bien tap Nhat Ky Ngay bang AI ^& day OTA len Link Co Dinh Vinh Vien:
echo       https://truongduc164.github.io/cyberbird-lingo/
python central_daily_watchdog.py --once

echo [2/2] Kich hoat Silent Watchdog chay ngam (5 phut/lan) tu dong update moi ngay...
wscript.exe "%~dp0START_SILENT_WATCHDOG.vbs"
echo       -^> Da san sang! Moi thiet bi (iPhone/Android/PC) tu dong nhan bai hoc moi
echo           tai: https://truongduc164.github.io/cyberbird-lingo/
start https://truongduc164.github.io/cyberbird-lingo/
