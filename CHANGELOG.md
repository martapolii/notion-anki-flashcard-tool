# Change log

This file records the repository changes made for each project version.

## v3 — 2026-09-30

### Notion to Anki sync behavior

- Treat Notion as the source of truth for `Front`/`Back` content and deck placement for existing cards.
- Update existing `Imported` notes when the corresponding Notion row changes, while preserving Anki tags the workflow does not manage.
- Delete matching Anki notes when a Notion row is marked `Rejected`; retain the rejected row so future syncs can find the note if needed.
- Move an `Imported` row to `Needs review` when its tagged Anki note is missing, rather than silently recreating a card someone removed. Set it back to `Ready` to intentionally add it again.
- Sync AnkiWeb after collection changes, including updates and deletions.
- Document behavior in both platform guides and add `Rejected`/`Needs review` configuration values to both environment templates.

## v2 — 2026-09-23

### Documentation

- Updated the main README to describe both Mac and Windows implementations and to organize their setup instructions into separate sections.
- Expanded the Windows setup guide with AnkiConnect installation, configuration, and restart steps.
- Added troubleshooting for an unreachable AnkiConnect server, a Notion `404 object_not_found` response, Windows task registration permissions, and visible PowerShell windows.
- Documented how to configure `.env`, run a manual sync, understand `SKIP already in Anki`, register or remove the scheduled task, and set up AnkiWeb.

### Windows sync behavior

- Set Python output to UTF-8 in the PowerShell runner so Unicode punctuation in card text does not cause Windows console encoding errors.
- Updated the Task Scheduler installer to launch PowerShell with its window hidden. Re-run the installer from an elevated PowerShell window to apply this setting to an existing task.
- Added a windowless Windows Script Host launcher for scheduled runs after the PowerShell window continued to flash despite the hidden-window switch.
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
