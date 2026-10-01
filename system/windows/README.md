# Windows 11 system setup

This folder contains the Windows implementation of the local Notion → Anki system. The Notion side is shared across operating systems and is documented in [`../../notion/README.md`](../../notion/README.md).

The system does not generate flashcard content. The Notion Lecture Flashcard Generator creates Flashcards database rows. This system adds `Ready` rows, keeps `Imported` notes synchronized with Notion, deletes notes for `Rejected` rows, creates organized Anki decks, and syncs AnkiWeb.

## Requirements

- Windows 11
- Python 3 with the Python launcher (`py`) or `python` available in PowerShell
- Anki Desktop for Windows
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed and enabled in Anki Desktop
- A Notion internal integration with access to the Flashcards database
- An AnkiWeb account signed in within Anki Desktop

Anki Desktop must be running for AnkiConnect to accept cards. The scheduled task can start Anki in the background if it can find `anki.exe`; if the runner starts it, it asks Anki to close after the sync. An Anki instance that was already running is left open. The Windows computer must be awake and online when the scheduled task runs.

## Configuration

Keep the project in a stable local folder. Cloud-synced folders can be used, but choose a path that is available while the scheduled task runs, including when offline.

In PowerShell, from this folder, create a private `.env` file from the template and open it for editing:

```powershell
Copy-Item env.example .env
notepad .env
```

Set at least:

```text
NOTION_TOKEN=your_internal_connection_token
NOTION_DATABASE_ID=your_flashcards_database_id
```

Share the Flashcards database with the Notion integration. If Anki is installed in a nonstandard location, also set:

```text
ANKI_EXE_PATH=C:\Path\To\anki.exe
```

The Status select needs `Ready`, `Imported`, `Rejected`, and `Needs review` options. The sync uses `Needs review` when an imported note has disappeared from Anki. The other settings in `env.example` control Notion property names, Anki deck naming, and automatic AnkiWeb syncing. Do not commit `.env` or share its token.

## Install and configure AnkiConnect

1. In Anki Desktop, install [AnkiConnect](https://ankiweb.net/shared/info/2055492159) from the add-on page.
2. Open **Tools → Add-ons**, select **AnkiConnect**, then open **Config**.
3. Keep the local API address and port at `127.0.0.1` and `8765`. Leave `apiKey` as `null`; this sync script does not use an API key. The other default settings, including `webCorsOriginList`, can stay as they are.
4. Save the configuration and restart Anki Desktop so AnkiConnect starts its local server.

The sync script connects to `http://127.0.0.1:8765`. AnkiConnect must be running in Anki Desktop for either a manual or scheduled sync.

## Manual test

Open Anki Desktop and confirm AnkiConnect is enabled. In PowerShell, from this folder, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run_anki_sync.ps1 -StartAnki
```

The runner loads `.env`, starts Anki hidden only if Anki is not already running, waits for AnkiConnect, then runs the Python sync script. If it started Anki, it closes that instance gracefully when the run ends, including when the sync reports an error. An Anki instance that was already open is left alone. The Python script uses only the standard library. It checks `Ready`, `Imported`, and `Rejected` Notion rows and uses each page's stable `notionid_...` tag to find its Anki note.

`Ready` creates a note if none exists, or updates the existing note, then changes the Notion status to `Imported`. The sync also updates existing `Imported` notes when their question, answer, Notion tags, or target deck changes in Notion, so you do not need to reset edited cards to `Ready`. It adds missing Notion tags and preserves tags it does not manage. `Rejected` deletes the matching Anki note(s) and leaves the Notion row rejected. An `Imported` row whose note is missing from Anki changes to `Needs review`; it is not recreated automatically. Set it to `Ready` to add it again.

Keep rejected rows in Notion: deleting a row outright removes the sync's way to identify and delete its Anki note. A successful run ends with a `Done.` summary. AnkiWeb syncing is requested after any Anki collection changes (add, update, or delete).

## Automatic scheduling

Open PowerShell **as the Windows account that should own the task**. If registration reports **Access is denied**, reopen PowerShell with **Run as administrator** and run these commands from the repository:

```powershell
Set-Location 'C:\GitRepos\notion-anki-flashcard-tool'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\system\windows\install_task_scheduler.ps1
```

This registers a task named `Notion-Anki-Sync` for the account running PowerShell and starts it once immediately. A successful install prints `Installed Windows Task Scheduler task: Notion-Anki-Sync`. After that it runs at login and every 15 minutes while you are logged in. The task uses a windowless Windows Script Host launcher for PowerShell, uses the project folder as its working directory, and starts Anki hidden only when no Anki process is already running. A newly started instance is closed after the sync; an instance you opened yourself stays open.

The updated behavior takes effect on the next run; you do not need to reinstall the scheduled task.

To remove the task, run:

```powershell
Set-Location 'C:\GitRepos\notion-anki-flashcard-tool'
.\system\windows\uninstall_task_scheduler.ps1
```

The install script accepts `-IntervalMinutes` to change the repeat interval, for example `-IntervalMinutes 30`.

## AnkiWeb and other devices

Complete the initial AnkiWeb setup manually in Anki Desktop on this Windows computer:

1. Sign in to the same AnkiWeb account used on your other devices.
2. Click Anki's Sync button once.
3. Choose **Upload** only if this collection is the authoritative copy.
4. Sign in to that same AnkiWeb account on your Mac and phone.

After that, the script calls AnkiConnect's AnkiWeb sync action after collection changes when `ANKIWEB_AUTO_SYNC=true`. Anki clients generally sync when their collections are opened or closed. Windows must be awake, online, logged in, and able to run Anki for the scheduled import and upload to occur.

## Logs and troubleshooting

For a visible run, start `run_anki_sync.ps1` manually from PowerShell. It prints progress and errors in that window. The scheduled task runs without a visible console, so use Task Scheduler's task history if you need to diagnose a scheduled run.

Look for:

```text
IMPORTED:
UPDATED from Notion:
DELETED rejected card(s) from Anki:
SYNCED Anki collection changes to AnkiWeb.
```

Common issues:

- **AnkiConnect unavailable or connection refused at `127.0.0.1:8765`:** confirm the add-on is enabled and restart Anki Desktop after installing it or changing its configuration.
- **Python not found:** install Python 3 and enable the Python launcher or add Python to PATH.
- **Anki not found:** set `ANKI_EXE_PATH` in `.env`, or start Anki Desktop manually.
- **Execution policy error:** use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current PowerShell window.
- **Notion returns `404 object_not_found`:** check that `NOTION_DATABASE_ID` is the Flashcards database ID and that the database has been shared with the integration named by the token in `.env`.
- **Task registration says `Access is denied`:** run PowerShell as administrator under the Windows account that should own the task, then run the installer again.
- **Anki stays open after a scheduled sync:** the runner closes only instances it started. If Anki was already open, the runner intentionally leaves it open.
- **Anki window appears during a scheduled sync:** the runner requests a hidden launch. Windows or the installed Anki build may still briefly show its window during startup; the runner closes its instance after the sync.
- **Sync conflict:** resolve it manually in Anki after checking which device has the authoritative collection. Do not blindly choose Upload or Download.
