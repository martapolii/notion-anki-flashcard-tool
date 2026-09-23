[CmdletBinding()]
param(
    [int]$IntervalMinutes = 15
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Runner = Join-Path $ProjectDir "run_anki_sync.ps1"
$TaskName = "Notion-Anki-Sync"

if (-not (Test-Path -LiteralPath (Join-Path $ProjectDir ".env"))) {
    throw "Missing .env file. Copy env.example to .env and fill it in before installing the task."
}

$powershell = (Get-Command powershell.exe).Source
$arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Runner`" -StartAnki"
$action = New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory $ProjectDir
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn
$repeatTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($logonTrigger, $repeatTrigger) `
    -Principal $principal -Settings $settings -Description "Imports Notion flashcards into Anki and syncs AnkiWeb." -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName
Write-Host "Installed Windows Task Scheduler task: $TaskName"
Write-Host "Runs at login and every $IntervalMinutes minutes."
