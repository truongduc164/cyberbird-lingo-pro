@echo off
chcp 65001 >nul
title CyberBird Lingo PRO v3.2.1 - Chot Bai Hoc AI Ngay (DEAN OPTIMIZE)
cd /d "%~dp0"

echo ====================================================================
echo   CYBERBIRD LINGO PRO v3.2.1 - CHOT SO BAI HOC AI THU CONG ^& CLOUD
echo   (Mac dinh da hen gio tu dong 17:30 cuoi ngay, KHONG chay ngam 24/7)
echo ====================================================================

echo [1/1] Dang tong ket Nhat Ky bang AI ^& day OTA len Link Co Dinh Vinh Vien:
echo       https://truongduc164.github.io/cyberbird-lingo/
python central_daily_watchdog.py --once

echo.
echo -^> Hoan tat! Tien trinh da tu tat sach (khong ton RAM nen).
start https://truongduc164.github.io/cyberbird-lingo/
