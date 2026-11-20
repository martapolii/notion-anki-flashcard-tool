# Windows 11 system setup

This folder contains the Windows implementation of the local Notion → Anki system. The Notion side is shared across operating systems and is documented in [`../../notion/README.md`](../../notion/README.md).

The system does not generate flashcard content. The Notion Lecture Flashcard Generator creates Flashcards database rows. The daily task imports `Ready` rows and deletes notes for `Rejected` rows. A weekly full check also reconciles `Imported` notes with Notion. The system creates course/week decks and syncs AnkiWeb.

Cards go into `course::Week N` decks. Session, chapter, and topic labels in
Notion do not create Anki subdecks. Known chapter-only rows use the mapping in
[`deck_naming.py`](deck_naming.py): COMP255 chapters 6–8 → weeks 6–8 and
chapters 9–10 → week 9; COMP307 chapters 7–9 → weeks 7–9; COMP231 chapter 10 →
week 6. `comp3231` is treated as `comp231`. An unmapped row is reported for
review without creating a chapter or topic deck.

COMP307 abbreviation rows have `Abbreviation` checked in Notion and are tagged
`comp307_abbreviations` in Anki while remaining in their week decks. Existing
rows whose old `Anki Deck` path ends in `Abbreviations` also retain the tag.
In Anki, open `comp307::Abbreviations` and choose **Rebuild**
to gather them for a focused session. Choose **Empty** afterward to return
unreviewed cards to their week decks. The importer leaves cards in this
filtered deck alone while it is active.

Use this scheduled importer on only one computer for a given Notion database and AnkiWeb collection. If the macOS importer is also scheduled, both local collections can import the same `Ready` row before syncing; AnkiWeb then merges separate notes and creates duplicates. Other devices should sync AnkiWeb without running the Notion importer.

## Requirements

- Windows 11
- Python 3 with the Python launcher (`py`) or `python` available in PowerShell
- Anki Desktop for Windows
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed and enabled in Anki Desktop
- A Notion internal integration with access to the Flashcards database
- An AnkiWeb account signed in within Anki Desktop

Anki Desktop must be running for AnkiConnect to accept cards. The scheduled task can start Anki minimized if it can find `anki.exe`; if the runner starts it, it asks Anki to close after the sync. An Anki instance that was already running is left open. The Windows computer must be awake and online when the scheduled task runs.

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

The Status select needs `Ready`, `Imported`, `Rejected`, `Needs review`, and `Duplicate` options. The sync uses `Needs review` when an imported note has disappeared from Anki and `Duplicate` when Anki refuses a new note with the same front. The other settings in `env.example` control Notion property names, Anki deck naming, and automatic AnkiWeb syncing. Do not commit `.env` or share its token.

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

The runner loads `.env`, starts Anki minimized only if Anki is not already running, waits for AnkiConnect, then runs the Python sync script. If it started Anki, it requests a graceful close and waits for the Anki app and API to exit when the run ends, including when the sync reports an error. An Anki instance that was already open is left alone. The Python script uses only the standard library. It normally checks `Ready` and `Rejected` rows and uses each page's stable `notionid_...` tag to find its Anki note.

Only `Ready` rows create Anki notes. When an existing row is marked `Ready`, its Notion Question and Answer update that Anki note's Front and Back; then the row returns to `Imported`. A full check also checks `Imported` rows to keep their deck and Notion tags synchronized, while preserving Anki Front/Back formatting. `Needs review`, `Duplicate`, and any other unrecognized status are skipped. Set `ANKI_SYNC_NOTE_FIELDS=true` in `.env` only if you want even the weekly `Imported` check to overwrite Anki fields. `Rejected` deletes matching Anki notes. An `Imported` row whose note is missing from Anki changes to `Needs review`; it is not recreated automatically. A `Ready` card Anki would refuse as a duplicate is marked `Duplicate` instead of forcing another copy.

Keep rejected rows in Notion: deleting a row outright removes the sync's way to identify and delete its Anki note. A successful run ends with a `Done.` summary. AnkiWeb syncing is requested after any Anki collection changes (add, update, or delete).

For content cleanup, review the question and answer before changing a status. Keep quiz-bank questions and course software-demo examples even when they revisit an earlier topic: they may be reused in later assessments. Mark a genuinely unwanted row `Rejected` so Anki can remove its note; keep the Notion row as the deletion record. To revise a card, edit its Question or Answer, then mark it `Ready` to send that wording to Anki. To restore a missing card in `Needs review`, mark it `Ready` after confirming that a new Anki note is wanted. Check a `Duplicate` row manually before changing its status.

## Automatic scheduling

Open PowerShell **as the Windows account that should own the task**. If registration reports **Access is denied**, reopen PowerShell with **Run as administrator** and run these commands from the repository:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\system\windows\install_task_scheduler.ps1
```

This registers a task named `Notion-Anki-Sync` for the account running PowerShell. A successful install prints `Installed Windows Task Scheduler task: Notion-Anki-Sync`. It runs once a day at 8:00 p.m. local time, or when available after a missed run while you are logged in. Normal runs check `Ready` and `Rejected` rows. On Saturday, or when a missed full check becomes due, it also checks `Imported` rows. Successful full checks are recorded locally to avoid repeating them within the week. Installation does not start an extra sync. The task uses a windowless Windows Script Host launcher for PowerShell, uses the project folder as its working directory, and starts Anki minimized only when no Anki process is already running. A newly started instance is closed after the sync; an instance you opened yourself stays open.

To request a full database check at any time, run `.\system\windows\run_anki_sync.ps1 -StartAnki -FullReconcile` from the repository root in PowerShell.

Run the installer again to replace an existing 15-minute task with the daily trigger. It replaces the task with the same name rather than creating a duplicate.

To remove the task, run:

```powershell
.\system\windows\uninstall_task_scheduler.ps1
```

The install script accepts `-DailyTime` in 24-hour local time, for example `-DailyTime "21:00"`.

## Deck migration and cleanup tools

The normal importer places cards in course/week decks, but it does not automatically remove old empty chapter or session decks. These one-time tools are separate from the daily task. Run them with Anki Desktop open, from `system/windows`, after confirming AnkiWeb has synced. If the COMP307 Abbreviations filtered deck is active, choose **Empty** in Anki before migrating so those cards return to their home decks.

1. Run `py -3 migrate_decks.py` for a preview. It reads `.env`, compares Notion rows with Anki notes by their stable `notionid_...` tags, and lists the proposed deck moves and unresolved rows. It does not edit card text or Notion rows.
2. Resolve any reported unknown or conflicting week in Notion. Run the preview again. To apply exactly that plan, run `py -3 migrate_decks.py --apply --expect N`, replacing `N` with the preview's **deck moves** count. The script refuses a changed count or unresolved weeks, moves cards, tags legacy COMP307 abbreviations, and syncs AnkiWeb.
3. Run `py -3 cleanup_empty_decks.py` to preview obsolete empty deck trees. Inspect every listed name: this tool treats any deck outside the configured course/week pattern as obsolete, including unrelated empty decks in the same Anki collection. It refuses a tree containing cards.
4. If the preview lists only decks you want removed, run `py -3 cleanup_empty_decks.py --apply --expect-roots R --expect-cards C`, using its **obsolete empty deck trees** count for `R` and **Cards** count for `C`. It rechecks both counts, removes only empty trees, verifies the card count, and syncs AnkiWeb.

`deck_naming.py` contains the shared course/week mapping used by the importer and migration preview. Run `py -3 -m unittest test_deck_naming.py` from `system/windows` to check that mapping and the importer's related behavior after changing it. `cleanup_empty_decks.py` uses the default local AnkiConnect address; if you changed `ANKI_CONNECT_URL`, set it in the PowerShell process before using that tool.

| File | Purpose |
| --- | --- |
| `anki_notion_sync.py` | Imports, updates, rejects, and reconciles Notion cards through AnkiConnect. |
| `deck_naming.py` | Resolves course/week destinations and rejects unknown or conflicting weeks. |
| `migrate_decks.py` | Previews or applies one-time moves from legacy decks. |
| `cleanup_empty_decks.py` | Previews or removes obsolete empty deck trees. |
| `test_deck_naming.py` | Checks deck mapping and key importer behavior. |
| `run_anki_sync.ps1` | Loads `.env`, chooses daily or full reconciliation, and runs the importer. |
| `run_anki_sync_hidden.vbs` | Starts the scheduled PowerShell runner without a console window. |
| `install_task_scheduler.ps1` / `uninstall_task_scheduler.ps1` | Registers or removes the daily Windows task. |
| `env.example` | Lists nonsecret configuration defaults for a private `.env`. |

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
- **Anki will not open after using v4:** v4 could leave a windowless `Anki.exe` running. In Task Manager, open **Details**, select `anki.exe`, choose **End task**, then open Anki from its desktop shortcut. The current runner detects this stranded state instead of silently using it.
- **Anki window appears during a scheduled sync:** Anki starts minimized so it can create its normal desktop window and exit cleanly after the sync. It may appear in the taskbar while the sync runs, but it should not take focus.
- **Sync conflict:** resolve it manually in Anki after checking which device has the authoritative collection. Do not blindly choose Upload or Download.
