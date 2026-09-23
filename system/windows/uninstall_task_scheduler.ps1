[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$TaskName = "Notion-Anki-Sync"
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Removed Windows Task Scheduler task: $TaskName"
