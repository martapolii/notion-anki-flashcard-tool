# Notion documentation

These files describe the current Notion side of the workflow. They are independent of the macOS Anki import system.

## Source-of-truth files

1. [`agent-setup-and-replication.md`](agent-setup-and-replication.md) is the current source of truth for the Lecture Flashcard Generator agent. It includes the current trigger, agent instructions, database structure, permissions, and replication checklist.
2. [`transcript-summary-instructions.md`](transcript-summary-instructions.md) is the current source of truth for the Notion AI summary prompts used for lectures, project/capstone classes, and textbook readings.

Use the exact current agent instructions in section 4 of the replication document. The agent currently uses:

- `Flashcard Generation = Generating` as the database trigger state.
- Summary content only, not full raw transcripts.
- Lecture and textbook summaries as equal flashcard sources.
- Key Terms sections as a source for dedicated definition cards.
- `Flashcard Run Notes` for per-run status and gaps.
- `Flashcard Generation = Generated` or `Error` as the completion state.

## Archived documentation

The files in [`archive`](archive) are retained for history only. They describe earlier workflows and should not be used for a new setup.

## Boundary with the system documentation

Notion is the source of truth for flashcard content and status. The local sync adds `Ready` rows, mirrors edits to `Imported` notes, and deletes the Anki notes for rows marked `Rejected`. If an `Imported` note is missing from Anki, its Notion row moves to `Needs review` rather than being recreated. Keep rejected rows in the database so the sync can identify the matching Anki note. See the platform setup guides in [`../system/macos/README.md`](../system/macos/README.md) and [`../system/windows/README.md`](../system/windows/README.md).
