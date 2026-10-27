@echo off
chcp 65001 >nul
title Video Automation Studio
cd /d "%~dp0"
echo ========================================================
echo   🎬 ANTIGRAVITY VIDEO AUTOMATION (REA ENGINE)
echo ========================================================
echo.
echo 1. Tao video tu dong theo chu de AI (Mac dinh)
echo 2. Nhap chu de cua rieng ban
echo 3. Chon file truyen/kich ban (.txt)
echo.
set /p choice="Nhap lua chon cua ban (1, 2, hoac 3): "

if "%choice%"=="2" (
    echo.
    set /p mytopic="Nhap chu de video: "
    python make_video.py --topic "%mytopic%"
) else if "%choice%"=="3" (
    echo.
    set /p myfile="Nhap duong dan file .txt: "
    python make_video.py --file "%myfile%"
) else (
    python make_video.py
)

echo.
echo Nhan phim bat ky de thoat...
pause >nul
