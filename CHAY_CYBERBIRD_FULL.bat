@echo off
chcp 65001 >nul
title CyberBird Lingo PRO v3.1.1 - Full Launcher (DEAN OPTIMIZE)
cd /d "%~dp0"

echo ==============================================================
echo   CYBERBIRD LINGO PRO v3.1.1 - DAILY TIMELINE ^& OFFLINE VAULT
echo ==============================================================

echo [1/3] Dong bo ngay du lieu Nhat Ky Ngay (Read-Only Z: Watchdog)...
python central_daily_watchdog.py --once
wscript.exe "%~dp0START_SILENT_WATCHDOG.vbs"
echo       -^> Da kich hoat Silent Watchdog chay ngam (5 phut/lan).

echo [2/3] Khoi dong Local Web Server tai http://127.0.0.1:8099 ...
start "CyberBird HTTP 8099" /min cmd /c "python -m http.server 8099 --directory cyberbird_lingo"

if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    echo [3/3] Mo Cloudflare Tunnel ^& tu dong gui Link + QR moi ve Telegram...
    python start_tunnel_and_notify.py
) else (
    echo [3/3] Mo trinh duyet tai http://127.0.0.1:8099 ...
    start http://127.0.0.1:8099
    pause
)
