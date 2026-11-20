[CmdletBinding()]
param(
    [ValidatePattern('^(?:[01][0-9]|2[0-3]):[0-5][0-9]$')]
    [string]$DailyTime = "20:00"
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName = "Notion-Anki-Sync"
$HiddenRunner = Join-Path $ProjectDir "run_anki_sync_hidden.vbs"

if (-not (Test-Path -LiteralPath (Join-Path $ProjectDir ".env"))) {
    throw "Missing .env file. Copy env.example to .env and fill it in before installing the task."
}

$windowsScriptHost = Join-Path $env:SystemRoot "System32\wscript.exe"
$arguments = "//B //NoLogo `"$HiddenRunner`""
$action = New-ScheduledTaskAction -Execute $windowsScriptHost -Argument $arguments -WorkingDirectory $ProjectDir
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.Add([TimeSpan]::Parse($DailyTime)))
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $dailyTrigger `
    -Principal $principal -Settings $settings -Description "Imports Notion flashcards into Anki and syncs AnkiWeb." `
    -Force -ErrorAction Stop | Out-Null

Write-Host "Installed Windows Task Scheduler task: $TaskName"
Write-Host "Runs daily at $DailyTime local time, or when available after a missed run."
