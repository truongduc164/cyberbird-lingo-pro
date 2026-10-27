@echo off
chcp 65001 >nul
title Bilingual Story Studio - 1-Click Video Maker
cd /d "%~dp0"

echo ========================================================
echo    Bilingual Story Studio - Video Generator
echo    Song Ngu Trung - Viet 9:16 Video Maker
echo ========================================================
echo.

set "PATH=C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin;%PATH%"

python make_story_video.py -i sample_story.txt -o Rua_Va_Tho_Song_Ngu.mp4

echo.
echo ========================================================
echo Video da duoc luu tai thu muc hien tai va Desktop!
echo ========================================================
pause
