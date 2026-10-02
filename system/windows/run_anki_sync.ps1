[CmdletBinding()]
param(
    [switch]$StartAnki
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path $ProjectDir ".env"
$PythonScript = Join-Path $ProjectDir "anki_notion_sync.py"

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Missing .env file. Copy env.example to .env and fill in your Notion values."
}

function Import-DotEnv([string]$Path) {
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) {
            continue
        }

        $separator = $trimmed.IndexOf("=")
        if ($separator -lt 1) {
            continue
        }

        $name = $trimmed.Substring(0, $separator).Trim()
        $value = $trimmed.Substring($separator + 1).Trim()
        if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

function Get-AnkiExecutable {
    $candidates = @(
        $env:ANKI_EXE_PATH,
        (Join-Path $env:LOCALAPPDATA "Programs\Anki\anki.exe"),
        (Join-Path $env:ProgramFiles "Anki\anki.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Anki\anki.exe")
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }
    return $null
}

function Test-AnkiConnect {
    try {
        $ankiUrl = $env:ANKI_CONNECT_URL
        if (-not $ankiUrl) {
            $ankiUrl = "http://127.0.0.1:8765"
        }
        $body = @{ action = "version"; version = 6 } | ConvertTo-Json -Compress
        $response = Invoke-RestMethod -Uri $ankiUrl `
            -Method Post -ContentType "application/json" -Body $body -TimeoutSec 5
        return ($null -eq $response.error)
    }
    catch {
        return $false
    }
}

Import-DotEnv $EnvFile
Set-Location -LiteralPath $ProjectDir
# Notion questions can contain Unicode punctuation that the Windows console
# code page cannot encode. Keep Python's output UTF-8 so one card cannot abort a run.
$env:PYTHONIOENCODING = "utf-8"

function Test-AnkiProcess {
    return [bool](Get-Process -Name "anki" -ErrorAction SilentlyContinue)
}

function Test-AnkiWindow {
    foreach ($process in Get-Process -Name "anki" -ErrorAction SilentlyContinue) {
        $process.Refresh()
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) {
            return $true
        }
    }
    return $false
}

$ankiConnectAvailable = Test-AnkiConnect
if ($ankiConnectAvailable -and (Test-AnkiProcess) -and -not (Test-AnkiWindow)) {
    throw "AnkiConnect is responding from a windowless Anki process. Close the stranded Anki.exe in Task Manager, then open Anki from its desktop shortcut."
}

$startedAnkiByRunner = $false
$startedAnkiProcess = $null
if ($StartAnki -and -not $ankiConnectAvailable) {
    if (-not (Test-AnkiProcess)) {
        $ankiPath = Get-AnkiExecutable
        if (-not $ankiPath) {
            throw "Anki executable not found. Set ANKI_EXE_PATH in .env or start Anki Desktop manually."
        }
        $startedAnkiProcess = Start-Process -FilePath $ankiPath `
            -WorkingDirectory (Split-Path -Parent $ankiPath) -WindowStyle Minimized -PassThru
        $startedAnkiByRunner = $true
    }
}

$pythonExitCode = 0
try {
    $deadline = (Get-Date).AddSeconds(60)
    while (-not (Test-AnkiConnect) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
    }

    if (-not (Test-AnkiConnect)) {
        throw "AnkiConnect is unavailable. Open Anki Desktop and confirm the AnkiConnect add-on is enabled."
    }

    $python = Get-Command py -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source -3 $PythonScript
    }
    else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            throw "Python was not found. Install Python 3 and enable the Python launcher or add Python to PATH."
        }
        & $python.Source $PythonScript
    }
    $pythonExitCode = $LASTEXITCODE
}
finally {
    if ($startedAnkiByRunner) {
        try {
            $connectDeadline = (Get-Date).AddSeconds(10)
            while (-not (Test-AnkiConnect) -and (Get-Date) -lt $connectDeadline) {
                Start-Sleep -Seconds 1
            }

            if (Test-AnkiConnect) {
                $ankiUrl = $env:ANKI_CONNECT_URL
                if (-not $ankiUrl) {
                    $ankiUrl = "http://127.0.0.1:8765"
                }
                $exitRequest = @{ action = "guiExitAnki"; version = 6 } | ConvertTo-Json -Compress
                Invoke-RestMethod -Uri $ankiUrl -Method Post -ContentType "application/json" `
                    -Body $exitRequest -TimeoutSec 5 | Out-Null
            }
            elseif ($startedAnkiProcess -and -not $startedAnkiProcess.HasExited) {
                [void]$startedAnkiProcess.CloseMainWindow()
            }

            # AnkiConnect's exit action is asynchronous. Wait for the actual app
            # and its API to stop; the process returned by Start-Process can be
            # only a launcher and may exit before Anki itself does.
            $shutdownDeadline = (Get-Date).AddSeconds(20)
            while (((Test-AnkiConnect) -or (Test-AnkiProcess)) `
                    -and (Get-Date) -lt $shutdownDeadline) {
                Start-Sleep -Seconds 1
            }

            if ((Test-AnkiConnect) -or (Test-AnkiProcess)) {
                foreach ($process in Get-Process -Name "anki" -ErrorAction SilentlyContinue) {
                    [void]$process.CloseMainWindow()
                }
                $shutdownDeadline = (Get-Date).AddSeconds(10)
                while (((Test-AnkiConnect) -or (Test-AnkiProcess)) `
                        -and (Get-Date) -lt $shutdownDeadline) {
                    Start-Sleep -Seconds 1
                }
            }

            if ((Test-AnkiConnect) -or (Test-AnkiProcess)) {
                Write-Warning "Anki is still running after a graceful close request. It was left alone rather than forcibly terminated."
            }
        }
        catch {
            Write-Warning "The sync finished, but the Anki instance started by this runner could not be closed gracefully: $_"
        }
    }
}

exit $pythonExitCode
