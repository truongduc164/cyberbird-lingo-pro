@echo off
chcp 65001 >nul
powershell -NoProfile -Command "Unregister-ScheduledTask -TaskName 'DeanOptimize_CyberBird_DailyDigest_1730' -Confirm:$false -ErrorAction SilentlyContinue"
echo Da tat lich tu dong chot bai hoc 17:30 hang ngay!
echo Khi nao muon bat lai, chay file CAIDAT_LICH_17H30_CUOI_GIO.ps1.
pause
