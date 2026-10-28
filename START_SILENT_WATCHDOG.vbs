' Chạy ngầm tàng hình ĐÚNG 1 LẦN chốt sổ cuối ngày (17:30) rồi tự thoát hoàn toàn (0 MB RAM nền!)
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = "pythonw.exe """ & scriptDir & "\central_daily_watchdog.py"" --scheduled"
shell.Run cmd, 0, False
