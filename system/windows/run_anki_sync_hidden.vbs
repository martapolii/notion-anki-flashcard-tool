Option Explicit

Dim shell, fileSystem, scriptDir, runnerPath, powershellPath, command, exitCode
Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

scriptDir = fileSystem.GetParentFolderName(WScript.ScriptFullName)
runnerPath = fileSystem.BuildPath(scriptDir, "run_anki_sync.ps1")
powershellPath = shell.ExpandEnvironmentStrings("%SystemRoot%") & _
    "\System32\WindowsPowerShell\v1.0\powershell.exe"

shell.CurrentDirectory = scriptDir
command = """" & powershellPath & """ -NoProfile -WindowStyle Hidden" & _
    " -ExecutionPolicy Bypass -File """ & runnerPath & """ -StartAnki"

exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode
