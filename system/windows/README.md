# Windows 11 system setup

This folder contains the Windows implementation of the local Notion → Anki system. The Notion side is shared across operating systems and is documented in [`../../notion/README.md`](../../notion/README.md).

The Windows system reads Flashcards database rows from Notion, imports them into Anki Desktop through AnkiConnect, repairs missing imports, and synchronizes AnkiWeb after successful imports.

## Requirements

- Windows 11
- Python 3 with the Python launcher (`py`) or `python` available in PowerShell
- Anki Desktop for Windows
- AnkiConnect installed and enabled in Anki Desktop
- A Notion internal integration with access to the Flashcards database
- An AnkiWeb account configured in Anki Desktop

Anki Desktop must be running for AnkiConnect to work. The scheduled runner can start Anki automatically if it can find `anki.exe`.

## 1. Copy the project and configure `.env`

Keep this repository in a stable local folder. iCloud Drive can be used for the repository, but the scheduled task should point to a local path if iCloud files may be unavailable while offline.

In PowerShell, from this folder:

```powershell
Copy-Item env.example .env
notepad .env
```

Set at least:

```text
NOTION_TOKEN=your_internal_connection_token
NOTION_DATABASE_ID=your_flashcards_database_id
```

If Anki is installed in a nonstandard location, also set:

```text
ANKI_EXE_PATH=C:\Path\To\anki.exe
```

Do not commit `.env`.

## 2. Test one run

Open Anki Desktop and make sure AnkiConnect is enabled. Then run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run_anki_sync.ps1 -StartAnki
```

The runner loads `.env`, waits for AnkiConnect, runs the shared Python sync logic, and returns the Python exit code.

## 3. Install automatic scheduling

Run PowerShell from this folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install_task_scheduler.ps1
```

This creates a task named `Notion-Anki-Sync` that runs at login and every 15 minutes. It runs only while your Windows user is logged in and can start Anki if it is not already open.

To remove it:

```powershell
.\uninstall_task_scheduler.ps1
```

## AnkiWeb and other devices

Complete the initial AnkiWeb setup manually in Anki Desktop on the Windows computer. Sign in to the same AnkiWeb account used by the Mac and phone, then choose **Upload** only if this collection is the authoritative copy. After that, the Python script calls AnkiConnect's AnkiWeb sync action after importing cards.

Anki on the phone and Mac will generally sync when their collections are opened or closed. The Windows computer must be awake, online, and able to run Anki for the scheduled import and AnkiWeb sync to occur.

## Troubleshooting

The Python script prints its output in the scheduled task context. For a visible test, run `run_anki_sync.ps1` manually from PowerShell.

Look for:

```text
IMPORTED/REPAIRED:
SYNCED Anki collection to AnkiWeb.
```

Common issues:

- **AnkiConnect unavailable:** open Anki Desktop and confirm the add-on is enabled.
- **Python not found:** install Python 3 and enable the Python launcher or add Python to PATH.
- **Anki not found:** set `ANKI_EXE_PATH` in `.env`.
- **Execution policy error:** use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current PowerShell window.
- **Sync conflict:** resolve it manually in Anki after checking which device has the authoritative collection.
