Set WshShell = CreateObject("WScript.Shell")
strCurrentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Check if Streamlit is already running on port 8501
' Launch batch script with normal window or minimized
WshShell.CurrentDirectory = strCurrentDir
WshShell.Run "cmd /c run_app.bat", 1, False
