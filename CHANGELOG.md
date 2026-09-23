# Change log

This file records the repository changes made for each project version.

## v2 — 2026-09-23

### Documentation

- Updated the main README to describe both Mac and Windows implementations and to organize their setup instructions into separate sections.
- Expanded the Windows setup guide with AnkiConnect installation, configuration, and restart steps.
- Added troubleshooting for an unreachable AnkiConnect server, a Notion `404 object_not_found` response, Windows task registration permissions, and visible PowerShell windows.
- Documented how to configure `.env`, run a manual sync, understand `SKIP already in Anki`, register or remove the scheduled task, and set up AnkiWeb.

### Windows sync behavior

- Set Python output to UTF-8 in the PowerShell runner so Unicode punctuation in card text does not cause Windows console encoding errors.
- Updated the Task Scheduler installer to launch PowerShell with its window hidden. Re-run the installer from an elevated PowerShell window to apply this setting to an existing task.
- Documented that Anki intentionally remains open after a scheduled sync starts it, as a visible cue that the sync ran and may have added flashcards.

### Windows setup notes

- The local `.env` contains the Notion integration configuration and is ignored by Git; it is not included in this change log or repository changes.
- AnkiConnect responded after it was installed and Anki Desktop was restarted.
- The sync completed with 183 eligible Notion rows already present in Anki; the final run imported no additional cards.
- The `Notion-Anki-Sync` task was registered and its first observed run succeeded. The installed task may need to be refreshed with the updated installer to hide its PowerShell window.

## v1 — baseline

- Notion generates flashcard rows; the local sync imports `Ready` rows into Anki and syncs AnkiWeb.
- The repository contained separate Mac and Windows scripts and setup guides, along with shared Notion workflow documentation.
- The main README incorrectly described the local system as macOS-only; v2 corrected that description and clarified the platform-specific setup paths.
