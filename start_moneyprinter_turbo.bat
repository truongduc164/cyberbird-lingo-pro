@echo off
chcp 65001 >nul
title MoneyPrinterTurbo - AI Video Maker
cd /d "%~dp0MoneyPrinterTurbo"
echo ========================================================
echo   🚀 MONEYPRINTERTURBO - ORIGINAL AI SHORT VIDEO MAKER
echo   Mo trinh duyet tai: http://127.0.0.1:8501
echo ========================================================
echo.
python -m streamlit run webui/Main.py --server.port=8501
pause
