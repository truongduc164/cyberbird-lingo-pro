# Cài đặt lịch tự động chốt sổ Bài Học AI định kỳ lúc 17:30 cuối giờ làm việc hằng ngày
# - Chạy tàng hình 1 lần ~15 giây rồi tự thoát hoàn toàn (0 MB RAM nền trong ngày!)
# - Bật StartWhenAvailable: nếu 17:30 máy đang tắt, lần mở máy kế tiếp (tối đó hoặc hôm sau) sẽ tự chạy bù 1 lần.

$TaskName = "DeanOptimize_CyberBird_DailyDigest_1730"
$VbsPath  = Join-Path $PSScriptRoot "START_SILENT_WATCHDOG.vbs"

$Action   = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`"" -WorkingDirectory $PSScriptRoot
$Trigger  = New-ScheduledTaskTrigger -Daily -At "17:30"
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "CyberBird Lingo PRO - Chot bai hoc AI dinh ky cuoi gio lam viec (17:30) & day OTA GitHub Pages" | Out-Null

$Info = Get-ScheduledTask -TaskName $TaskName
$Next = (Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime
Write-Output ("INSTALLED TASK: " + $Info.TaskName + " | State: " + $Info.State + " | NextRunTime: " + $Next)
