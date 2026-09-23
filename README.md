# Notion → Anki Flashcard Tool

This project has two separate parts:

1. **Notion** creates academic flashcards from lecture and textbook summaries.
2. **A local computer system** imports those cards into Anki and syncs AnkiWeb.

The current system implementation is macOS-only. Windows documentation and scripts will be added separately later.

## Documentation

### Notion workflow

- [Notion setup and replication](notion/agent-setup-and-replication.md) — the current source of truth for the Lecture Flashcard Generator agent, triggers, permissions, databases, and properties.
- [Notion AI transcript-summary instructions](notion/transcript-summary-instructions.md) — current Lecture, Project/Capstone, and Textbook summary instructions.
- [Agent instructions pointer](notion/agent-instructions.md) — points to the current instructions inside the replication document.

The files in [`notion/archive`](notion/archive) are historical versions and are not part of the current setup.

### Local system workflow

- [macOS system setup](system/macos/README.md) — Python, AnkiConnect, `.env`, LaunchAgent automation, AnkiWeb syncing, and troubleshooting.
- [Windows 11 system setup](system/windows/README.md) — Python, AnkiConnect, PowerShell, Task Scheduler automation, AnkiWeb syncing, and troubleshooting.
- [`system/macos/anki_notion_sync.py`](system/macos/anki_notion_sync.py) — imports and repairs cards through AnkiConnect.
- [`system/macos/env.example`](system/macos/env.example) — safe configuration template.

## High-level flow

```text
Notion AI transcript summaries
        ↓
Lecture Flashcard Generator agent
        ↓
Notion Flashcards database (Status = Ready)
        ↓
macOS LaunchAgent or Windows Task Scheduler
        + Python sync script
        ↓
Anki Desktop through AnkiConnect
        ↓
AnkiWeb
        ↓
Phone and Windows Anki clients
```

The Notion agent does not call Anki directly. The macOS system reads the Flashcards database through the Notion API, creates course/week decks in Anki, prevents duplicate imports with stable Notion page tags, and syncs the collection to AnkiWeb after successful imports.

## Current Anki organization

Course codes remain lowercase. A card with `Anki Deck = comp307` and `Week = W1` is placed in:

```text
comp307::Week 1
```

A value such as `W1 (2)` becomes:

```text
comp307::Week 1::Session 2
```
