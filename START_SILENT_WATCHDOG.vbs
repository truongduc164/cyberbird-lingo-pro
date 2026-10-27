Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = "pythonw.exe """ & scriptDir & "\central_daily_watchdog.py"" --daemon --interval 300"
shell.Run cmd, 0, False
